from fastapi import APIRouter, Request, Response, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from supertokens_python.recipe.emailpassword.asyncio import sign_in, sign_up
from supertokens_python.recipe.session.asyncio import create_new_session
from supertokens_python.recipe.emailverification.asyncio import create_email_verification_token, verify_email_using_token
import logging

from app.core.database import get_db
from app.services.database_service import UserService
from app.models.mongo_models import Invitation, User as MongoUser

logger = logging.getLogger(__name__)

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
        
        # Determine role based on invitation status
        user_role = "member" if is_invited else "admin"
        logger.info(f"Setting user role: {user_role} (is_invited: {is_invited})")
        
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
            await UserService.create_user_with_profile(
                db=db,
                supertokens_id=supertokens_user.id,
                email=supertokens_user.emails[0],
                profile_data=profile_data
            )
            logger.info("User created successfully in database")

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
            return JSONResponse(status_code=500, content={"status": "ERROR", "message": f"Signup failed: {error_status}"})
            
    except Exception as e:
        logger.error(f"Sign-up error: {str(e)}", exc_info=True)
        return JSONResponse(status_code=500, content={"status": "ERROR", "message": f"An unexpected server error occurred: {str(e)}"})


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
        return JSONResponse(status_code=500, content={"status": "ERROR", "message": f"Server error: {str(e)}"})
