from fastapi import APIRouter, Request, Response, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from supertokens_python.recipe.emailpassword.asyncio import sign_in, sign_up, send_reset_password_email, reset_password_using_token
from supertokens_python.recipe.session.asyncio import create_new_session
from supertokens_python.recipe.emailverification.asyncio import create_email_verification_token, verify_email_using_token
import logging

from app.core.database import get_db
from app.core.config import settings
from app.core.email_domains import get_email_domain, is_blocked_domain
from app.services.database_service import UserService
from app.services import otp_service
from app.services.email_verification_service import send_otp_email
from app.models.mongo_models import Invitation, User as MongoUser

logger = logging.getLogger(__name__)


def sanitize_error_message(error: Exception) -> str:
    """
    Sanitize error messages to prevent exposing sensitive database/system information.
    Always log the full error but return a generic message to the user.
    """
    error_str = str(error).lower()

    if "unique" in error_str or "duplicate" in error_str or "already exists" in error_str:
        if "email" in error_str:
            return "An account with this email already exists."
        return "This record already exists."

    if "foreign key" in error_str:
        return "Invalid reference to related data."

    if "not null" in error_str:
        return "Required information is missing."

    return "An unexpected error occurred. Please try again later."


router = APIRouter()


# ═══════════════════════════════════════════════════════════════════════════
# SIGNUP
# ═══════════════════════════════════════════════════════════════════════════

@router.post("/custom-signup")
async def post_signup(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    """
    Handles creating the user in SuperTokens and our databases.

    Admin path:
      - Creates account, sends 6-digit OTP to email for verification.
      - Returns { requiresOTPVerification: true, email }.
      - No session created.

    Member path (invite token present):
      - Creates account, auto-verifies email (invite proves identity).
      - Creates SuperTokens session immediately.
      - Returns { requiresEmailVerification: false }.
    """
    try:
        logger.info("Starting sign-up process")
        body = await request.json()
        email = body.get("email")
        password = body.get("password")

        logger.info(f"Sign-up attempt for email: {email}")

        if not email or not password:
            return JSONResponse(status_code=400, content={"status": "ERROR", "message": "Email and password required"})

        email_domain = get_email_domain(email)
        if not email_domain:
            return JSONResponse(status_code=400, content={"status": "ERROR", "message": "Invalid email address"})

        if is_blocked_domain(email_domain, settings.BLOCKED_EMAIL_DOMAINS):
            return JSONResponse(
                status_code=403,
                content={"status": "ERROR", "message": "Please use your company email or request an invite from your organization."}
            )

        # Check if user already exists BEFORE calling SuperTokens
        existing_pg_user = await UserService.get_user_by_email_pg(db, email)
        
        if existing_pg_user:
            if existing_pg_user.is_verified:
                return JSONResponse(status_code=409, content={"status": "ERROR", "message": "An account with this email already exists."})
            else:
                logger.info(f"Unverified user {email} trying to sign up again. Deleting old records.")
                # Delete from SuperTokens
                if existing_pg_user.supertokens_id:
                    try:
                        from supertokens_python.asyncio import delete_user
                        await delete_user(existing_pg_user.supertokens_id)
                    except Exception as e:
                        logger.warning(f"Could not delete SuperTokens user: {e}")
                
                # Delete from PG
                await UserService.delete_user_pg(db, existing_pg_user.id)
                
                # Delete from Mongo
                existing_mongo_user = await MongoUser.find_one(MongoUser.email == email)
                if existing_mongo_user:
                    await existing_mongo_user.delete()
                
                # Reset invitation if it exists so member can reuse their invite link
                from app.models.mongo_models import Invitation
                invitation = await Invitation.find_one(Invitation.email == email)
                if invitation and invitation.used:
                    invitation.used = False
                    await invitation.save()
        else:
            existing_mongo_user = await MongoUser.find_one(MongoUser.email == email)
            if existing_mongo_user:
                return JSONResponse(status_code=409, content={"status": "ERROR", "message": "An account with this email already exists."})

        invite_token = body.get("inviteToken")
        is_invited = bool(invite_token)
        organization_id = None

        if invite_token:
            from app.services import invitation_service
            invitation = await invitation_service.validate_invitation(invite_token)
            if not invitation:
                return JSONResponse(status_code=400, content={"status": "ERROR", "message": "Invalid or expired invitation token"})

            if invitation.email != email:
                return JSONResponse(status_code=400, content={"status": "ERROR", "message": "Email does not match invitation"})

            inviter_domain = get_email_domain(invitation.invited_by_email)
            if inviter_domain and inviter_domain != email_domain:
                return JSONResponse(
                    status_code=403,
                    content={"status": "ERROR", "message": "Please use your company email that matches your organization's domain."}
                )

            inviter = await MongoUser.find_one(MongoUser.email == invitation.invited_by_email)
            if inviter and inviter.organization_id:
                organization_id = inviter.organization_id
                logger.info(f"Found inviter's organization: {organization_id}")

        required_fields = ["firstName", "lastName", "email", "password", "companyName", "industrySector", "companySize", "city"]
        if not all(body.get(f) for f in required_fields):
            return JSONResponse(status_code=400, content={"status": "ERROR", "message": "Missing required fields"})

        explicit_role = body.get("role")
        user_role = explicit_role if explicit_role else ("member" if is_invited else "admin")

        profile_data = {
            "name": f"{body.get('firstName')} {body.get('lastName')}",
            "company": body.get("companyName"),
            "industry_sector": body.get("industrySector"),
            "company_size": body.get("companySize"),
            "location": body.get("city"),
            "title": body.get("title"),
            "role": user_role,
            "organization_id": organization_id
        }

        logger.info("Calling SuperTokens sign_up")
        supertokens_result = await sign_up("public", email, password)

        from supertokens_python.recipe.emailpassword.interfaces import SignUpOkResult

        if isinstance(supertokens_result, SignUpOkResult):
            supertokens_user = supertokens_result.user
            logger.info(f"SuperTokens user created with ID: {supertokens_user.id}")

            try:
                await UserService.create_user_with_profile(
                    db=db,
                    supertokens_id=supertokens_user.id,
                    email=supertokens_user.emails[0],
                    profile_data=profile_data
                )
            except ValueError as ve:
                logger.error(f"Organization validation failed: {str(ve)}")
                try:
                    from supertokens_python.asyncio import delete_user
                    await delete_user(supertokens_user.id)
                except Exception as delete_error:
                    logger.warning(f"Could not delete SuperTokens user: {delete_error}")
                return JSONResponse(status_code=400, content={"status": "ERROR", "message": str(ve)})

            # ── Send OTP for email verification (Both Admin & Member) ─────────────
            try:
                plain_code, challenge_id = await otp_service.create_otp(db, email, "signup_verify")
                await send_otp_email(email, plain_code, "signup_verify")
                logger.info(f"Signup OTP sent to: {email}")
            except Exception as e:
                logger.error(f"Failed to send signup OTP: {str(e)}")
                # User is created — return success so they can use resend

            return JSONResponse(status_code=200, content={
                "status": "OK",
                "message": "Account created. Please check your email for a 6-digit verification code.",
                "requiresOTPVerification": True,
                "email": email
            })

        elif hasattr(supertokens_result, 'status') and supertokens_result.status == "EMAIL_ALREADY_EXISTS_ERROR":
            return JSONResponse(status_code=409, content={"status": "ERROR", "message": "Email already exists"})
        else:
            error_status = getattr(supertokens_result, 'status', 'Unknown error')
            logger.error(f"Sign-up failed with status: {error_status}")
            return JSONResponse(status_code=500, content={"status": "ERROR", "message": "Signup failed. Please try again or contact support."})

    except IntegrityError as e:
        logger.error(f"Sign-up database integrity error: {str(e)}", exc_info=True)
        return JSONResponse(status_code=409, content={"status": "ERROR", "message": "An account with this email already exists."})
    except Exception as e:
        logger.error(f"Sign-up error: {str(e)}", exc_info=True)
        safe_message = sanitize_error_message(e)
        return JSONResponse(status_code=500, content={"status": "ERROR", "message": safe_message})


# ═══════════════════════════════════════════════════════════════════════════
# SIGNUP OTP VERIFICATION
# ═══════════════════════════════════════════════════════════════════════════

@router.post("/verify-signup-otp")
async def verify_signup_otp(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    """
    Verify the 6-digit code sent after admin signup.
    On success, marks the email as verified in SuperTokens.
    Frontend should redirect to /login afterwards.
    """
    try:
        body = await request.json()
        email = body.get("email", "").strip().lower()
        code = body.get("code", "").strip()

        if not email or not code:
            return JSONResponse(status_code=400, content={"status": "ERROR", "message": "Email and code are required"})

        result = await otp_service.verify_otp(db, email, code, "signup_verify")

        if not result["ok"]:
            error = result["error"]
            if error == "OTP_EXPIRED":
                return JSONResponse(status_code=400, content={
                    "status": "OTP_EXPIRED",
                    "message": "Your verification code has expired. Please request a new one."
                })
            elif error == "MAX_ATTEMPTS_REACHED":
                return JSONResponse(status_code=429, content={
                    "status": "MAX_ATTEMPTS_REACHED",
                    "message": "Too many incorrect attempts. Please request a new code."
                })
            elif error == "INVALID_CODE":
                remaining = result.get("attempts_remaining", 0)
                return JSONResponse(status_code=400, content={
                    "status": "INVALID_CODE",
                    "message": f"Incorrect code. {remaining} attempt{'s' if remaining != 1 else ''} remaining.",
                    "attemptsRemaining": remaining
                })
            else:
                return JSONResponse(status_code=400, content={
                    "status": "ERROR",
                    "message": "Invalid or expired verification code. Please request a new one."
                })

        # Mark email as verified in SuperTokens
        auto_login_success = False
        try:
            pg_user = await UserService.get_user_by_email_pg(db, email)
            if pg_user and pg_user.supertokens_id:
                from supertokens_python.asyncio import get_user
                st_user = await get_user(pg_user.supertokens_id)
                if st_user and st_user.login_methods:
                    recipe_user_id = st_user.login_methods[0].recipe_user_id
                    token_result = await create_email_verification_token("public", recipe_user_id, email)
                    if hasattr(token_result, 'token'):
                        await verify_email_using_token("public", token_result.token)
                        logger.info(f"Email verified in SuperTokens for: {email}")

                # Also update is_verified in our DB
                pg_user.is_verified = True
                await db.commit()

                # ---- NEW: Auto-login after signup verification ----
                session = await create_new_session(request, "public", recipe_user_id)
                logger.info(f"Session created for new admin {email}: {session.get_handle()}")

                # Create trusted device record + set cookie (same as login)
                device_token = await otp_service.create_trusted_device(db, email)
                from datetime import timedelta
                from app.services.otp_service import _now_utc
                expires = _now_utc() + timedelta(days=settings.TRUSTED_DEVICE_DAYS)
                
                response.set_cookie(
                    key="trusted_device",
                    value=device_token,
                    httponly=True,
                    secure=settings.ENVIRONMENT != "development",
                    samesite="lax",
                    expires=int(expires.timestamp()),
                    max_age=settings.TRUSTED_DEVICE_DAYS * 24 * 3600,
                )

                auto_login_success = True

        except Exception as e:
            logger.error(f"Failed to mark email verified/auto-login in SuperTokens: {str(e)}", exc_info=True)

        # Mark invitation as used after successful OTP verification
        try:
            from datetime import datetime
            invitation = await Invitation.find_one(Invitation.email == email, Invitation.used == False)
            if invitation:
                invitation.used = True
                invitation.used_at = datetime.utcnow()
                await invitation.save()
                logger.info(f"Marked invitation as used for: {email}")
        except Exception as e:
            logger.warning(f"Could not mark invitation for {email}: {e}")

        import json
        response.status_code = 200
        response.body = json.dumps({
            "status": "OK",
            "message": (
                "Email verified successfully! You are now signed in."
                if auto_login_success else
                "Email verified successfully! Please sign in to continue."
            ),
            "requiresManualLogin": not auto_login_success,
        }).encode()
        response.headers["content-type"] = "application/json"
        return response

    except Exception as e:
        logger.error(f"Verify signup OTP error: {str(e)}", exc_info=True)
        return JSONResponse(status_code=500, content={"status": "ERROR", "message": sanitize_error_message(e)})


# ═══════════════════════════════════════════════════════════════════════════
# SIGNIN (device-aware MFA)
# ═══════════════════════════════════════════════════════════════════════════

@router.post("/custom-signin")
async def post_signin(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    """
    Step 1 of device-aware MFA login.

    Flow:
      1. Verify email + password with SuperTokens.
      2. Confirm email is verified.
      3. Check for a valid 'trusted_device' cookie.
         - If valid trusted device → create session immediately (no OTP).
         - If no/invalid trusted device → send OTP, return MFA_REQUIRED.
    """
    try:
        logger.info("Starting sign-in process")
        body = await request.json()
        email = body.get("email", "").strip().lower()
        password = body.get("password", "")

        if not email or not password:
            return JSONResponse(status_code=400, content={"status": "ERROR", "message": "Email and password required"})

        from app.core.email_domains import get_email_domain, is_blocked_domain
        from app.core.config import settings
        
        email_domain = get_email_domain(email)
        if email_domain and is_blocked_domain(email_domain, settings.BLOCKED_EMAIL_DOMAINS):
            logger.warning(f"Login attempt blocked for personal email domain: {email}")
            return JSONResponse(
                status_code=403,
                content={"status": "ERROR", "message": "Personal email addresses are not allowed. Please use your company email."}
            )

        result = await sign_in("public", email, password)

        from supertokens_python.recipe.emailpassword.interfaces import SignInOkResult

        if isinstance(result, SignInOkResult):
            user = result.user
            logger.info(f"Password verified for user: {user.id}")

            # Check email verification
            from supertokens_python.recipe.emailverification.asyncio import is_email_verified
            email_verified = await is_email_verified(result.recipe_user_id)
            if not email_verified:
                logger.warning(f"Login attempt with unverified email: {email}")
                return JSONResponse(
                    status_code=403,
                    content={
                        "status": "EMAIL_NOT_VERIFIED",
                        "message": "Please verify your email before logging in.",
                        "email": email
                    }
                )

            # ── Check trusted device cookie ─────────────────────────────────────
            device_token = request.cookies.get("trusted_device", "")
            is_trusted = await otp_service.validate_trusted_device(db, email, device_token)

            if is_trusted:
                # Known device — skip OTP, create session immediately
                logger.info(f"Trusted device recognised for {email} — skipping MFA")
                session = await create_new_session(request, "public", result.recipe_user_id)
                logger.info(f"Session created (trusted device): {session.get_handle()}")

                import json
                response.status_code = 200
                response.body = json.dumps({"status": "OK", "message": "Login successful!"}).encode()
                response.headers["content-type"] = "application/json"
                return response

            # ── New/unknown device — send OTP ───────────────────────────────────
            logger.info(f"New device for {email} — sending login MFA OTP")
            plain_code, challenge_id = await otp_service.create_otp(db, email, "login_mfa")
            await send_otp_email(email, plain_code, "login_mfa")

            return JSONResponse(status_code=200, content={
                "status": "MFA_REQUIRED",
                "message": "A verification code has been sent to your email.",
                "challengeId": challenge_id,
                "email": email
            })

        else:
            result_type_name = type(result).__name__
            if "WrongCredentials" in result_type_name or "WRONG_CREDENTIALS" in str(result):
                return JSONResponse(status_code=401, content={"status": "ERROR", "message": "Invalid email or password"})
            else:
                logger.error(f"Unexpected sign-in result type: {type(result)}")
                return JSONResponse(status_code=500, content={"status": "ERROR", "message": "Authentication failed"})

    except Exception as e:
        logger.error(f"Sign-in error: {str(e)}", exc_info=True)
        return JSONResponse(status_code=500, content={"status": "ERROR", "message": sanitize_error_message(e)})


# ═══════════════════════════════════════════════════════════════════════════
# LOGIN OTP VERIFICATION
# ═══════════════════════════════════════════════════════════════════════════

@router.post("/verify-login-otp")
async def verify_login_otp(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    """
    Step 2 of MFA login: verify the OTP sent during /custom-signin.
    On success:
      - Creates a SuperTokens session.
      - Creates a TrustedDevice record.
      - Sets a long-lived 'trusted_device' HttpOnly cookie.
    """
    try:
        body = await request.json()
        email = body.get("email", "").strip().lower()
        challenge_id = body.get("challengeId", "").strip()
        code = body.get("code", "").strip()

        if not email or not challenge_id or not code:
            return JSONResponse(status_code=400, content={"status": "ERROR", "message": "email, challengeId and code are required"})

        result = await otp_service.verify_otp(db, email, code, "login_mfa", challenge_id=challenge_id)

        if not result["ok"]:
            error = result["error"]
            if error == "OTP_EXPIRED":
                return JSONResponse(status_code=400, content={
                    "status": "OTP_EXPIRED",
                    "message": "Your login code has expired. Please sign in again."
                })
            elif error == "MAX_ATTEMPTS_REACHED":
                return JSONResponse(status_code=429, content={
                    "status": "MAX_ATTEMPTS_REACHED",
                    "message": "Too many incorrect attempts. Please sign in again to get a new code."
                })
            elif error == "INVALID_CODE":
                remaining = result.get("attempts_remaining", 0)
                return JSONResponse(status_code=400, content={
                    "status": "INVALID_CODE",
                    "message": f"Incorrect code. {remaining} attempt{'s' if remaining != 1 else ''} remaining.",
                    "attemptsRemaining": remaining
                })
            else:
                return JSONResponse(status_code=400, content={
                    "status": "ERROR",
                    "message": "Invalid or expired code. Please sign in again."
                })

        # OTP valid — find the user and create session
        pg_user = await UserService.get_user_by_email_pg(db, email)
        if not pg_user or not pg_user.supertokens_id:
            return JSONResponse(status_code=404, content={"status": "ERROR", "message": "User not found"})

        from supertokens_python.asyncio import get_user as st_get_user
        st_user = await st_get_user(pg_user.supertokens_id)
        if not st_user or not st_user.login_methods:
            return JSONResponse(status_code=404, content={"status": "ERROR", "message": "User not found in auth system"})

        recipe_user_id = st_user.login_methods[0].recipe_user_id

        # Create SuperTokens session
        session = await create_new_session(request, "public", recipe_user_id)
        logger.info(f"Session created after MFA for {email}: {session.get_handle()}")

        # Create trusted device record + set cookie
        device_token = await otp_service.create_trusted_device(db, email)

        from datetime import timedelta
        from app.services.otp_service import _now_utc
        expires = _now_utc() + timedelta(days=settings.TRUSTED_DEVICE_DAYS)

        response.set_cookie(
            key="trusted_device",
            value=device_token,
            httponly=True,
            secure=settings.ENVIRONMENT != "development",
            samesite="lax",
            expires=int(expires.timestamp()),
            max_age=settings.TRUSTED_DEVICE_DAYS * 24 * 3600,
        )

        import json
        response.status_code = 200
        response.body = json.dumps({"status": "OK", "message": "Login successful!"}).encode()
        response.headers["content-type"] = "application/json"
        return response

    except Exception as e:
        logger.error(f"Verify login OTP error: {str(e)}", exc_info=True)
        return JSONResponse(status_code=500, content={"status": "ERROR", "message": sanitize_error_message(e)})


# ═══════════════════════════════════════════════════════════════════════════
# RESEND OTP
# ═══════════════════════════════════════════════════════════════════════════

@router.post("/resend-otp")
async def resend_otp(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Resend a 6-digit OTP code.
    Rate-limited to once per OTP_RESEND_COOLDOWN_SECONDS.
    """
    try:
        body = await request.json()
        email = body.get("email", "").strip().lower()
        purpose = body.get("purpose", "").strip()

        if not email or purpose not in ("signup_verify", "login_mfa"):
            return JSONResponse(status_code=400, content={"status": "ERROR", "message": "Valid email and purpose are required"})

        try:
            plain_code, challenge_id = await otp_service.create_otp(db, email, purpose)
            await send_otp_email(email, plain_code, purpose)
            logger.info(f"OTP resent for {email} purpose={purpose}")
        except ValueError as ve:
            err = str(ve)
            if err.startswith("RATE_LIMITED:"):
                seconds = int(err.split(":")[1])
                return JSONResponse(status_code=429, content={
                    "status": "RATE_LIMITED",
                    "message": f"Please wait {seconds} seconds before requesting a new code.",
                    "retryAfterSeconds": seconds
                })
            raise

        return JSONResponse(status_code=200, content={
            "status": "OK",
            "message": "A new code has been sent to your email.",
            "challengeId": challenge_id
        })

    except Exception as e:
        logger.error(f"Resend OTP error: {str(e)}", exc_info=True)
        return JSONResponse(status_code=500, content={"status": "ERROR", "message": sanitize_error_message(e)})


# ═══════════════════════════════════════════════════════════════════════════
# FORGOT / RESET PASSWORD (unchanged)
# ═══════════════════════════════════════════════════════════════════════════

@router.post("/forgot-password")
async def forgot_password(request: Request, db: AsyncSession = Depends(get_db)):
    """Handles forgot password request — sends reset email with token"""
    try:
        body = await request.json()
        email = body.get("email")

        if not email:
            return JSONResponse(status_code=400, content={"status": "ERROR", "message": "Email is required"})

        try:
            pg_user = await UserService.get_user_by_email_pg(db, email)

            if not pg_user or not pg_user.supertokens_id:
                return JSONResponse(
                    status_code=200,
                    content={"status": "OK", "message": "If an account exists with this email, a password reset link has been sent."}
                )

            await send_reset_password_email("public", pg_user.supertokens_id, email)
            logger.info(f"Password reset email sent to: {email}")

            return JSONResponse(
                status_code=200,
                content={"status": "OK", "message": "If an account exists with this email, a password reset link has been sent."}
            )
        except Exception as e:
            logger.error(f"Failed to send reset email: {str(e)}")
            return JSONResponse(
                status_code=200,
                content={"status": "OK", "message": "If an account exists with this email, a password reset link has been sent."}
            )

    except Exception as e:
        logger.error(f"Forgot password error: {str(e)}", exc_info=True)
        return JSONResponse(status_code=500, content={"status": "ERROR", "message": sanitize_error_message(e)})


@router.post("/reset-password")
async def reset_password(request: Request):
    """Handles password reset using token from email"""
    try:
        body = await request.json()
        token = body.get("token")
        new_password = body.get("newPassword")

        if not token or not new_password:
            return JSONResponse(status_code=400, content={"status": "ERROR", "message": "Token and new password are required"})

        result = await reset_password_using_token("public", token, new_password)
        result_type_name = type(result).__name__

        if "InvalidToken" in result_type_name:
            return JSONResponse(
                status_code=400,
                content={"status": "ERROR", "message": "Invalid or expired reset token. Please request a new password reset link."}
            )
        elif "PasswordPolicyViolation" in result_type_name:
            failure_reason = getattr(result, 'failure_reason', 'Password does not meet requirements')
            return JSONResponse(
                status_code=400,
                content={
                    "status": "FIELD_ERROR",
                    "message": "Password must be at least 8 characters long and contain a mix of letters and numbers.",
                    "formFields": [{"id": "password", "error": str(failure_reason)}]
                }
            )
        elif "Ok" in result_type_name:
            user_id = getattr(result, 'user_id', None)
            return JSONResponse(
                status_code=200,
                content={"status": "OK", "message": "Password has been reset successfully. You can now log in with your new password.", "userId": user_id}
            )
        else:
            logger.error(f"Unknown password reset result type: {result_type_name}")
            return JSONResponse(
                status_code=400,
                content={"status": "ERROR", "message": "Password reset failed. Please try again or request a new reset link."}
            )

    except Exception as e:
        logger.error(f"Password reset error: {str(e)}", exc_info=True)
        return JSONResponse(status_code=500, content={"status": "ERROR", "message": sanitize_error_message(e)})


# ═══════════════════════════════════════════════════════════════════════════
# CUSTOM SIGNOUT (Clear trusted device)
# ═══════════════════════════════════════════════════════════════════════════

@router.post("/custom-signout")
async def custom_signout(request: Request, response: Response):
    """
    Clears the trusted_device cookie when the user logs out manually.
    This ensures that OTP will be required on the next login.
    """
    try:
        import json
        response.status_code = 200
        response.set_cookie(
            key="trusted_device",
            value="",
            httponly=True,
            secure=settings.ENVIRONMENT != "development",
            samesite="lax",
            expires=0,
            max_age=0,
        )
        response.body = json.dumps({"status": "OK", "message": "Signout preparation complete."}).encode()
        response.headers["content-type"] = "application/json"
        return response
    except Exception as e:
        logger.error(f"Custom signout error: {str(e)}", exc_info=True)
        return JSONResponse(status_code=500, content={"status": "ERROR", "message": sanitize_error_message(e)})
