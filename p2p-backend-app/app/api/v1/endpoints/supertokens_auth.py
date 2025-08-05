from fastapi import APIRouter, Request, Response
from fastapi.responses import HTMLResponse
from supertokens_python.recipe.emailpassword.asyncio import sign_in, sign_up  
from supertokens_python.recipe.session.asyncio import create_new_session

router = APIRouter()

# OPTIONS handlers for CORS preflight
@router.options("/custom-signin")
async def options_signin():
    """Handle CORS preflight for custom signin"""
    return {"message": "CORS preflight handled"}

@router.options("/custom-signup") 
async def options_signup():
    """Handle CORS preflight for custom signup"""
    return {"message": "CORS preflight handled"}

@router.get("/custom-signin", response_class=HTMLResponse)
async def get_signin_page():
    """Return a SIMPLE HTML signin form - NO JAVASCRIPT ISSUES"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sign In - SIMPLE VERSION</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                max-width: 400px; 
                margin: 50px auto; 
                padding: 20px; 
                background-color: #f5f5f5;
            }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input { 
                width: 95%; 
                padding: 10px; 
                border: 2px solid #007bff; 
                border-radius: 4px; 
                font-size: 16px;
            }
            button { 
                width: 100%; 
                padding: 12px; 
                background-color: #007bff; 
                color: white; 
                border: none; 
                border-radius: 4px; 
                font-size: 16px;
                cursor: pointer;
            }
            button:hover { background-color: #0056b3; }
        </style>
    </head>
    <body>
        <h2>🔐 Sign In (SIMPLE TEST)</h2>
        <div class="form-group">
            <label>Email:</label>
            <input type="email" id="email" placeholder="Enter your email" required />
        </div>
        <div class="form-group">
            <label>Password:</label>
            <input type="password" id="password" placeholder="Enter your password" required />
        </div>
        <button onclick="testSignIn()">Sign In</button>
        
        <script>
        function testSignIn() {
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            if (!email || !password) {
                alert('Please fill both fields!');
                return;
            }
            
            alert('TEST: Email=' + email + ', Password=' + password);
            
            // Now try the actual API call
            fetch('/api/v1/auth/custom-signin', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            })
            .then(response => response.json())
            .then(result => {
                if (result.status === 'OK') {
                    alert('✅ LOGIN SUCCESS: ' + result.message);
                } else {
                    alert('❌ LOGIN FAILED: ' + result.message);
                }
            })
            .catch(error => {
                alert('🚨 ERROR: ' + error.message);
            });
        }
        </script>
    </body>
    </html>
    """

@router.post("/custom-signin")
async def post_signin(request: Request, response: Response):
    """Handle signin POST request - REAL SUPERTOKENS VERSION"""
    try:
        body = await request.json()
        email = body.get("email")
        password = body.get("password")
        
        if not email or not password:
            return {"status": "ERROR", "message": "Email and password required"}
        
        # 🔐 REAL SUPERTOKENS AUTHENTICATION
        print(f"🔍 Attempting SuperTokens sign_in for: {email}")
        result = await sign_in("public", email, password)
        print(f"🔍 SuperTokens sign_in result: {result}")
        
        # Handle different result types
        if hasattr(result, 'status'):
            print(f"🔍 Result status: {result.status}")
            if result.status == "OK":
                # Extract user info properly
                user_id = result.user.id
                user_email = result.user.emails[0] if result.user.emails else email
                print(f"🔍 Extracted user - ID: {user_id}, Email: {user_email}")
                
                # Create real SuperTokens session
                print(f"🔍 Creating session with recipe_user_id: {result.recipe_user_id}")
                session_result = await create_new_session(request, response, result.recipe_user_id)
                print(f"🔍 Session created: {session_result}")
                
                success_response = {
                    "status": "OK", 
                    "message": "Login successful!", 
                    "user": {
                        "id": user_id,
                        "email": user_email
                    }
                }
                print(f"🔍 Returning success response: {success_response}")
                return success_response
            elif result.status == "WRONG_CREDENTIALS_ERROR":
                return {"status": "ERROR", "message": "Invalid email or password"}
            else:
                return {"status": "ERROR", "message": f"Authentication failed: {result.status}"}
        else:
            return {"status": "ERROR", "message": "Unexpected response format"}
            
    except Exception as e:
        return {"status": "ERROR", "message": f"Server error: {str(e)}"}

@router.get("/custom-signup", response_class=HTMLResponse)
async def get_signup_page():
    """Return a SIMPLE HTML signup form - NO JAVASCRIPT ISSUES"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sign Up - SIMPLE VERSION</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                max-width: 400px; 
                margin: 50px auto; 
                padding: 20px; 
                background-color: #f5f5f5;
            }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input { 
                width: 95%; 
                padding: 10px; 
                border: 2px solid #28a745; 
                border-radius: 4px; 
                font-size: 16px;
            }
            button { 
                width: 100%; 
                padding: 12px; 
                background-color: #28a745; 
                color: white; 
                border: none; 
                border-radius: 4px; 
                font-size: 16px;
                cursor: pointer;
            }
            button:hover { background-color: #218838; }
        </style>
    </head>
    <body>
        <h2>📝 Sign Up (SIMPLE TEST)</h2>
        <div class="form-group">
            <label>Email:</label>
            <input type="email" id="email" placeholder="Enter your email" required />
        </div>
        <div class="form-group">
            <label>Password:</label>
            <input type="password" id="password" placeholder="Enter your password" required />
        </div>
        <div class="form-group">
            <label>First Name:</label>
            <input type="text" id="firstName" placeholder="Enter first name" required />
        </div>
        <div class="form-group">
            <label>Last Name:</label>
            <input type="text" id="lastName" placeholder="Enter last name" required />
        </div>
        <button onclick="testSignUp()">Sign Up</button>
        
        <script>
        function testSignUp() {
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const firstName = document.getElementById('firstName').value;
            const lastName = document.getElementById('lastName').value;
            
            if (!email || !password || !firstName || !lastName) {
                alert('Please fill all fields!');
                return;
            }
            
            alert('TEST: Email=' + email + ', Name=' + firstName + ' ' + lastName);
            
            // Now try the actual API call
            fetch('/api/v1/auth/custom-signup', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password, firstName, lastName })
            })
            .then(response => response.json())
            .then(result => {
                if (result.status === 'OK') {
                    alert('✅ SIGNUP SUCCESS: ' + result.message);
                } else {
                    alert('❌ SIGNUP FAILED: ' + result.message);
                }
            })
            .catch(error => {
                alert('🚨 ERROR: ' + error.message);
            });
        }
        </script>
    </body>
    </html>
    """

@router.post("/custom-signup")
async def post_signup(request: Request, response: Response):
    """Handle signup POST request - REAL SUPERTOKENS VERSION"""
    try:
        body = await request.json()
        email = body.get("email")
        password = body.get("password")
        first_name = body.get("firstName")
        last_name = body.get("lastName")
        
        if not all([email, password, first_name, last_name]):
            return {"status": "ERROR", "message": "All fields required"}
        
        # 🔐 REAL SUPERTOKENS SIGNUP
        result = await sign_up("public", email, password)
        
        # Handle different result types
        if hasattr(result, 'status'):
            if result.status == "OK":
                # Extract user info properly
                user_id = result.user.id
                user_email = result.user.emails[0] if result.user.emails else email
                
                # Create real SuperTokens session
                await create_new_session(request, response, result.recipe_user_id)
                
                return {
                    "status": "OK", 
                    "message": "Signup successful!", 
                    "user": {
                        "id": user_id,
                        "email": user_email,
                        "name": f"{first_name} {last_name}"
                    }
                }
            elif result.status == "EMAIL_ALREADY_EXISTS_ERROR":
                return {"status": "ERROR", "message": "Email already exists"}
            else:
                return {"status": "ERROR", "message": f"Signup failed: {result.status}"}
        else:
            return {"status": "ERROR", "message": "Unexpected response format"}
            
    except Exception as e:
        return {"status": "ERROR", "message": f"Server error: {str(e)}"}