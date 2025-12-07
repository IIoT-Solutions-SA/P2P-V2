from fastapi import APIRouter, Request, Response, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from supertokens_python.recipe.emailpassword.asyncio import sign_in, sign_up, send_reset_password_email, reset_password_using_token
from supertokens_python.recipe.session.asyncio import create_new_session
from supertokens_python.recipe.emailverification.asyncio import create_email_verification_token, verify_email_using_token
import logging

from app.core.database import get_db
from app.services.database_service import UserService
from app.models.mongo_models import Invitation, User as MongoUser

logger = logging.getLogger(__name__)


def sanitize_error_message(error: Exception) -> str:
    """
    Sanitize error messages to prevent exposing sensitive database/system information.
    Always log the full error but return a generic message to the user.
    """
    error_str = str(error).lower()

    # Check for common database constraint violations
    if "unique" in error_str or "duplicate" in error_str or "already exists" in error_str:
        if "email" in error_str:
            return "An account with this email already exists."
        return "This record already exists."

    if "foreign key" in error_str:
        return "Invalid reference to related data."

    if "not null" in error_str:
        return "Required information is missing."

    # Default generic message - NEVER expose the actual error
    return "An unexpected error occurred. Please try again later."

router = APIRouter()

@router.post("/custom-signup")
async def post_signup(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Handles creating the user in SuperTokens and our databases.
    It does NOT create a session. It returns a simple success status.
    """
    try:
        logger.info("Starting sign-up process")
        body = await request.json()
        email = body.get("email")
        password = body.get("password")
        
        logger.info(f"Sign-up attempt for email: {email}")

        # SECURITY: Check if user already exists in our database BEFORE calling SuperTokens
        existing_pg_user = await UserService.get_user_by_email_pg(db, email)
        if existing_pg_user:
            logger.warning(f"Signup attempt for existing email: {email}")
            return JSONResponse(status_code=409, content={"status": "ERROR", "message": "An account with this email already exists."})

        # Also check MongoDB for existing user
        existing_mongo_user = await MongoUser.find_one(MongoUser.email == email)
        if existing_mongo_user:
            logger.warning(f"Signup attempt for existing email (MongoDB): {email}")
            return JSONResponse(status_code=409, content={"status": "ERROR", "message": "An account with this email already exists."})

        # Check if this is an invited member signup - presence of token is what matters
        invite_token = body.get("inviteToken")
        is_invited = bool(invite_token)  # If there's a token, they're invited
        
        # Log what we received
        logger.info(f"Received signup request - inviteToken: {invite_token}, is_invited: {is_invited}")
        organization_id = None
        
        # If invited, validate and get the organization from the inviter
        if invite_token:
            from app.services import invitation_service
            from datetime import datetime
            
            # Validate the invitation
            invitation = await invitation_service.validate_invitation(invite_token)
            if not invitation:
                logger.error(f"Invalid or expired invitation token: {invite_token}")
                return JSONResponse(status_code=400, content={"status": "ERROR", "message": "Invalid or expired invitation token"})
            
            # Check if email matches
            if invitation.email != email:
                logger.error(f"Email mismatch: invitation for {invitation.email}, signup with {email}")
                return JSONResponse(status_code=400, content={"status": "ERROR", "message": "Email does not match invitation"})
                
            # Get the inviter's user to find their organization
            inviter = await MongoUser.find_one(MongoUser.email == invitation.invited_by_email)
            if inviter and inviter.organization_id:
                organization_id = inviter.organization_id
                logger.info(f"Found inviter's organization: {organization_id}")
            else:
                logger.warning(f"Could not find organization for inviter: {invitation.invited_by_email}")
        
        # Determine role based on invitation status or explicit role override (for seeding)
        explicit_role = body.get("role")  # Allow explicit role for seeding
        user_role = explicit_role if explicit_role else ("member" if is_invited else "admin")
        logger.info(f"Setting user role: {user_role} (is_invited: {is_invited}, explicit: {explicit_role})")
        
        profile_data = {
            "name": f"{body.get('firstName')} {body.get('lastName')}",
            "company": body.get("companyName"),
            "industry_sector": body.get("industrySector"),
            "company_size": body.get("companySize"),
            "location": body.get("city"),
            "title": body.get("title"),
            # Set role based on whether they're invited or creating new org
            "role": user_role,
            # Pass organization_id if this is an invited member
            "organization_id": organization_id
        }
        
        logger.info(f"Profile data being sent: role={profile_data['role']}, org_id={profile_data['organization_id']}")

        required_fields = [
            "firstName", "lastName", "email", "password",
            "companyName", "industrySector", "companySize", "city"
        ]
        if not all(body.get(f) for f in required_fields):
            logger.warning("Missing required fields in sign-up")
            return JSONResponse(status_code=400, content={"status": "ERROR", "message": "Missing required fields"})

        logger.info("Calling SuperTokens sign_up")
        supertokens_result = await sign_up("public", email, password)
        logger.info(f"SuperTokens sign_up result status: {getattr(supertokens_result, 'status', 'NO_STATUS')}")
        
        # Import the result types to check properly
        from supertokens_python.recipe.emailpassword.interfaces import SignUpOkResult
        
        if isinstance(supertokens_result, SignUpOkResult):
            supertokens_user = supertokens_result.user
            logger.info(f"SuperTokens user created with ID: {supertokens_user.id}")

            logger.info("Creating user in database")
            try:
                await UserService.create_user_with_profile(
                    db=db,
                    supertokens_id=supertokens_user.id,
                    email=supertokens_user.emails[0],
                    profile_data=profile_data
                )
                logger.info("User created successfully in database")
            except ValueError as ve:
                # Duplicate admin error - delete the SuperTokens user and return error
                logger.error(f"Organization validation failed: {str(ve)}")
                try:
                    from supertokens_python.asyncio import delete_user
                    await delete_user(supertokens_user.id)
                except Exception as delete_error:
                    logger.warning(f"Could not delete SuperTokens user: {delete_error}")
                return JSONResponse(
                    status_code=400,
                    content={
                        "status": "ERROR",
                        "message": str(ve)
                    }
                )

            # Handle email verification based on user type
            if invite_token:
                # Invited members: Mark invitation as used and verify email automatically
                from app.services import invitation_service
                await invitation_service.mark_invitation_used(invite_token)
                logger.info(f"Marked invitation as used: {invite_token}")

                # Automatically verify email for invited members (they received invite email)
                try:
                    from supertokens_python.recipe.emailverification.syncio import unverify_email, create_email_verification_token as sync_create_token
                    from supertokens_python.recipe.emailverification.asyncio import verify_email_using_token

                    # Create and immediately verify token for invited members
                    token_result = await create_email_verification_token("public", supertokens_result.recipe_user_id, email)
                    if hasattr(token_result, 'token'):
                        await verify_email_using_token("public", token_result.token)
                        logger.info(f"Automatically verified email for invited member: {email}")
                except Exception as e:
                    logger.warning(f"Could not auto-verify invited member email: {str(e)}")

                return JSONResponse(status_code=200, content={
                    "status": "OK",
                    "message": "User created successfully.",
                    "requiresEmailVerification": False
                })
            else:
                # Admin signup: Send verification email
                logger.info(f"Admin signup - sending verification email to: {email}")

                try:
                    from supertokens_python.recipe.emailverification.asyncio import send_email_verification_email

                    # Manually trigger verification email send
                    # Parameters: tenant_id, user_id, recipe_user_id, email
                    await send_email_verification_email(
                        "public",
                        supertokens_user.id,
                        supertokens_result.recipe_user_id,
                        email
                    )
                    logger.info(f"Verification email sent successfully to: {email}")
                except Exception as e:
                    logger.error(f"Failed to send verification email: {str(e)}")
                    # Still return success - user is created, they can resend email later

                return JSONResponse(status_code=200, content={
                    "status": "OK",
                    "message": "User created successfully. Please check your email to verify your account.",
                    "requiresEmailVerification": True,
                    "email": email
                })
            
        elif hasattr(supertokens_result, 'status') and supertokens_result.status == "EMAIL_ALREADY_EXISTS_ERROR":
            logger.warning("Email already exists during sign-up")
            return JSONResponse(status_code=409, content={"status": "ERROR", "message": "Email already exists"})
        else:
            error_status = getattr(supertokens_result, 'status', 'Unknown error')
            logger.error(f"Sign-up failed with status: {error_status}")
            return JSONResponse(status_code=500, content={"status": "ERROR", "message": "Signup failed. Please try again or contact support."})
            
    except IntegrityError as e:
        # Database constraint violation - likely duplicate email
        logger.error(f"Sign-up database integrity error: {str(e)}", exc_info=True)
        return JSONResponse(status_code=409, content={"status": "ERROR", "message": "An account with this email already exists."})
    except Exception as e:
        # SECURITY: Log the full error but return a sanitized message to prevent info leakage
        logger.error(f"Sign-up error: {str(e)}", exc_info=True)
        safe_message = sanitize_error_message(e)
        return JSONResponse(status_code=500, content={"status": "ERROR", "message": safe_message})


@router.post("/custom-signin")
async def post_signin(request: Request, response: Response):
    """Handles the custom sign-in flow and creates the session."""
    try:
        logger.info("Starting sign-in process")
        body = await request.json()
        email = body.get("email")
        password = body.get("password")
        
        logger.info(f"Sign-in attempt for email: {email}")
        
        if not email or not password:
            logger.warning("Missing email or password")
            return JSONResponse(status_code=400, content={"status": "ERROR", "message": "Email and password required"})
        
        logger.info("Calling SuperTokens sign_in")
        result = await sign_in("public", email, password)
        logger.info(f"SuperTokens sign_in result type: {type(result)}")
        logger.info(f"SuperTokens sign_in result attributes: {dir(result)}")
        
        # Import the result types to check properly
        from supertokens_python.recipe.emailpassword.interfaces import SignInOkResult
        
        if isinstance(result, SignInOkResult):
            user = result.user
            logger.info(f"Sign-in successful for user ID: {user.id}")
            logger.info(f"Recipe user ID: {result.recipe_user_id}")

            # Check if email is verified
            from supertokens_python.recipe.emailverification.asyncio import is_email_verified

            email_verified = await is_email_verified(result.recipe_user_id)
            logger.info(f"Email verification status for {email}: {email_verified}")

            if not email_verified:
                logger.warning(f"Login attempt with unverified email: {email}")
                return JSONResponse(
                    status_code=403,
                    content={
                        "status": "EMAIL_NOT_VERIFIED",
                        "message": "Please verify your email before logging in. Check your inbox for the verification link.",
                        "email": email
                    }
                )

            # Create session using the FastAPI response object
            logger.info("Creating new session")
            # Use the recipe_user_id from the result, not the user.id string
            session = await create_new_session(request, response, result.recipe_user_id)
            logger.info(f"Session created with handle: {session.get_handle()}")

            # Set the response body manually
            response.status_code = 200
            import json
            response_data = {"status": "OK", "message": "Login successful!", "userId": user.id}
            response.body = json.dumps(response_data).encode()
            response.headers["content-type"] = "application/json"

            logger.info("Returning response with session cookies")
            logger.info(f"Response headers: {dict(response.headers)}")
            return response
        else:
            # Check if it's a wrong credentials error by checking the type name
            result_type_name = type(result).__name__
            logger.info(f"Result type name: {result_type_name}")
            
            if "WrongCredentials" in result_type_name or "WRONG_CREDENTIALS" in str(result):
                logger.warning("Wrong credentials provided")
                return JSONResponse(status_code=401, content={"status": "ERROR", "message": "Invalid email or password"})
            else:
                logger.error(f"Unexpected sign-in result type: {type(result)}")
                return JSONResponse(status_code=500, content={"status": "ERROR", "message": "Authentication failed"})
            
    except Exception as e:
        logger.error(f"Sign-in error: {str(e)}", exc_info=True)
        safe_message = sanitize_error_message(e)
        return JSONResponse(status_code=500, content={"status": "ERROR", "message": safe_message})


@router.post("/forgot-password")
async def forgot_password(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Handles forgot password request - sends reset email with token
    """
    try:
        logger.info("Starting forgot password process")
        body = await request.json()
        email = body.get("email")

        logger.info(f"Forgot password request for email: {email}")

        if not email:
            logger.warning("Missing email in forgot password request")
            return JSONResponse(status_code=400, content={"status": "ERROR", "message": "Email is required"})

        # Look up the user to get their SuperTokens ID
        try:
            pg_user = await UserService.get_user_by_email_pg(db, email)

            if not pg_user or not pg_user.supertokens_id:
                logger.info(f"No user found with email: {email}")
                # Return success anyway to avoid revealing if email exists
                return JSONResponse(
                    status_code=200,
                    content={
                        "status": "OK",
                        "message": "If an account exists with this email, a password reset link has been sent."
                    }
                )

            # Send password reset email using SuperTokens with correct parameters
            # Parameters: tenant_id, user_id, email
            logger.info(f"Sending password reset email via SuperTokens for user_id: {pg_user.supertokens_id}")
            await send_reset_password_email("public", pg_user.supertokens_id, email)
            logger.info(f"Password reset email sent successfully to: {email}")

            return JSONResponse(
                status_code=200,
                content={
                    "status": "OK",
                    "message": "If an account exists with this email, a password reset link has been sent."
                }
            )
        except Exception as e:
            logger.error(f"Failed to send reset email: {str(e)}")
            # Still return success to avoid revealing if email exists
            return JSONResponse(
                status_code=200,
                content={
                    "status": "OK",
                    "message": "If an account exists with this email, a password reset link has been sent."
                }
            )

    except Exception as e:
        logger.error(f"Forgot password error: {str(e)}", exc_info=True)
        safe_message = sanitize_error_message(e)
        return JSONResponse(status_code=500, content={"status": "ERROR", "message": safe_message})


@router.post("/reset-password")
async def reset_password(request: Request):
    """
    Handles password reset using token from email
    """
    try:
        logger.info("Starting password reset process")
        body = await request.json()
        token = body.get("token")
        new_password = body.get("newPassword")

        logger.info(f"Password reset attempt with token")

        if not token or not new_password:
            logger.warning("Missing token or password in reset request")
            return JSONResponse(status_code=400, content={"status": "ERROR", "message": "Token and new password are required"})

        # Reset password using SuperTokens
        logger.info("Attempting to reset password with token")
        result = await reset_password_using_token("public", token, new_password)

        # Log result details for debugging
        logger.info(f"Reset password result type: {type(result)}")
        logger.info(f"Reset password result type name: {type(result).__name__}")
        if hasattr(result, 'status'):
            logger.info(f"Reset password result status: {result.status}")

        # Check if the reset failed
        # Check by type name since we can't import the specific result classes
        result_type_name = type(result).__name__
        logger.info(f"Reset password result: {result_type_name}, full result: {result}")

        if "InvalidToken" in result_type_name:
            logger.warning(f"Password reset failed - invalid token: {result_type_name}")
            return JSONResponse(
                status_code=400,
                content={
                    "status": "ERROR",
                    "message": "Invalid or expired reset token. Please request a new password reset link."
                }
            )
        elif "PasswordPolicyViolation" in result_type_name:
            # Password doesn't meet requirements
            failure_reason = getattr(result, 'failure_reason', 'Password does not meet requirements')
            logger.warning(f"Password reset failed - policy violation: {failure_reason}")
            return JSONResponse(
                status_code=400,
                content={
                    "status": "FIELD_ERROR",
                    "message": "Password must be at least 8 characters long and contain a mix of letters and numbers.",
                    "formFields": [{"id": "password", "error": str(failure_reason)}]
                }
            )
        elif "Ok" in result_type_name:
            # Success case - matches ResetPasswordUsingTokenOkResult
            user_id = getattr(result, 'user_id', None)
            logger.info(f"Password reset successful for user ID: {user_id}")
            return JSONResponse(
                status_code=200,
                content={
                    "status": "OK",
                    "message": "Password has been reset successfully. You can now log in with your new password.",
                    "userId": user_id
                }
            )
        else:
            # Unknown result type - log and return generic error
            logger.error(f"Unknown password reset result type: {result_type_name}")
            return JSONResponse(
                status_code=400,
                content={
                    "status": "ERROR",
                    "message": "Password reset failed. Please try again or request a new reset link."
                }
            )

    except Exception as e:
        logger.error(f"Password reset error: {str(e)}", exc_info=True)
        safe_message = sanitize_error_message(e)
        return JSONResponse(status_code=500, content={"status": "ERROR", "message": safe_message})


@router.post("/resend-verification-email")
async def resend_verification_email(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Resend email verification link to user
    Accepts email in request body
    """
    try:
        logger.info("Starting resend verification email process")
        body = await request.json()
        email = body.get("email")

        if not email:
            logger.warning("Missing email in resend verification request")
            return JSONResponse(
                status_code=400,
                content={"status": "ERROR", "message": "Email is required"}
            )

        logger.info(f"Resend verification email request for: {email}")

        # Look up the user to get their SuperTokens ID
        try:
            pg_user = await UserService.get_user_by_email_pg(db, email)

            if not pg_user or not pg_user.supertokens_id:
                logger.info(f"No user found with email: {email}")
                # Return success anyway to avoid revealing if email exists
                return JSONResponse(
                    status_code=200,
                    content={
                        "status": "OK",
                        "message": "If an account exists with this email and is not yet verified, a verification email has been sent."
                    }
                )

            # Check if email is already verified
            from supertokens_python.recipe.emailverification.asyncio import is_email_verified
            from supertokens_python.asyncio import get_user

            # Get the full user object to access recipe_user_id
            supertokens_user = await get_user(pg_user.supertokens_id)
            if not supertokens_user:
                logger.warning(f"Could not find SuperTokens user for ID: {pg_user.supertokens_id}")
                return JSONResponse(
                    status_code=200,
                    content={
                        "status": "OK",
                        "message": "If an account exists with this email and is not yet verified, a verification email has been sent."
                    }
                )

            # Get the recipe_user_id from the first login method
            if not supertokens_user.login_methods or len(supertokens_user.login_methods) == 0:
                logger.warning(f"No login methods found for user: {pg_user.supertokens_id}")
                return JSONResponse(
                    status_code=200,
                    content={
                        "status": "OK",
                        "message": "If an account exists with this email and is not yet verified, a verification email has been sent."
                    }
                )

            recipe_user_id = supertokens_user.login_methods[0].recipe_user_id

            # Check if already verified
            email_verified = await is_email_verified(recipe_user_id)
            if email_verified:
                logger.info(f"Email already verified for: {email}")
                return JSONResponse(
                    status_code=200,
                    content={
                        "status": "OK",
                        "message": "Email is already verified. You can log in now."
                    }
                )

            # Create verification token and send via our custom email service
            logger.info(f"Creating verification token for: {email}")
            token_result = await create_email_verification_token("public", recipe_user_id, email)

            if not hasattr(token_result, 'token'):
                logger.error(f"Failed to create verification token for: {email}")
                raise Exception("Could not create verification token")

            # Build verification URL
            from app.core.config import settings
            verification_url = f"{settings.WEBSITE_DOMAIN}/auth/verify-email?token={token_result.token}&tenantId=public"

            # Send using our custom email service
            from app.services.email_verification_service import send_email_verification
            logger.info(f"Sending verification email to: {email}")
            await send_email_verification(
                email=email,
                email_verify_url=verification_url
            )
            logger.info(f"Verification email sent successfully to: {email}")

            return JSONResponse(
                status_code=200,
                content={
                    "status": "OK",
                    "message": "Verification email has been sent. Please check your inbox."
                }
            )

        except Exception as e:
            logger.error(f"Failed to send verification email: {str(e)}")
            # Still return success to avoid revealing if email exists
            return JSONResponse(
                status_code=200,
                content={
                    "status": "OK",
                    "message": "If an account exists with this email and is not yet verified, a verification email has been sent."
                }
            )

    except Exception as e:
        logger.error(f"Resend verification email error: {str(e)}", exc_info=True)
        safe_message = sanitize_error_message(e)
        return JSONResponse(
            status_code=500,
            content={"status": "ERROR", "message": safe_message}
        )
