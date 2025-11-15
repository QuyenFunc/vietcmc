from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from datetime import datetime
import logging
from passlib.context import CryptContext

from app.database import get_db
from app.models import Client
from app.schemas import ClientRegisterRequest, ClientRegisterResponse, APIResponse
from app.utils.auth import generate_credentials

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/register", response_class=HTMLResponse)
async def get_register_form():
    """Display registration form"""
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VietCMS - Client Registration</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 500px;
            width: 100%;
            padding: 40px;
        }
        h1 { color: #333; margin-bottom: 10px; font-size: 28px; }
        .subtitle { color: #666; margin-bottom: 30px; font-size: 14px; }
        .form-group { margin-bottom: 20px; }
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 500;
            font-size: 14px;
        }
        input {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            transition: all 0.3s;
        }
        input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        button {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        .result {
            margin-top: 30px;
            padding: 20px;
            border-radius: 8px;
            display: none;
        }
        .result.success {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
        }
        .result.error {
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
        }
        .result h3 { margin-bottom: 10px; font-size: 16px; }
        .credential {
            background: rgba(0,0,0,0.05);
            padding: 10px;
            border-radius: 4px;
            margin: 8px 0;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            word-break: break-all;
        }
        .credential strong {
            display: block;
            margin-bottom: 4px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
        }
        .spinner {
            border: 3px solid rgba(255,255,255,0.3);
            border-radius: 50%;
            border-top: 3px solid white;
            width: 20px;
            height: 20px;
            animation: spin 1s linear infinite;
            display: inline-block;
            margin-right: 10px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 VietCMS Client Registration</h1>
        <p class="subtitle">Register your organization to get API credentials</p>
        
        <form id="registerForm">
            <div class="form-group">
                <label for="organization_name">Organization Name *</label>
                <input type="text" id="organization_name" required placeholder="e.g., Acme Corp">
            </div>
            
            <div class="form-group">
                <label for="email">Email Address *</label>
                <input type="email" id="email" required placeholder="admin@example.com">
            </div>
            
            <div class="form-group">
                <label for="password">Password *</label>
                <input type="password" id="password" required minlength="8" placeholder="Min 8 characters">
            </div>
            
            <div class="form-group">
                <label for="webhook_url">Webhook URL *</label>
                <input type="url" id="webhook_url" required placeholder="https://your-domain.com/webhook">
            </div>
            
            <button type="submit" id="submitBtn">Register</button>
        </form>
        
        <div id="result" class="result"></div>
    </div>
    
    <script>
        const form = document.getElementById('registerForm');
        const resultDiv = document.getElementById('result');
        const submitBtn = document.getElementById('submitBtn');
        
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = {
                organization_name: document.getElementById('organization_name').value,
                email: document.getElementById('email').value,
                password: document.getElementById('password').value,
                webhook_url: document.getElementById('webhook_url').value
            };
            
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner"></span>Registering...';
            resultDiv.style.display = 'none';
            
            try {
                const response = await fetch('/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'ngrok-skip-browser-warning': 'true'
                    },
                    body: JSON.stringify(formData)
                });
                
                const data = await response.json();
                
                if (response.ok && data.success) {
                    resultDiv.className = 'result success';
                    resultDiv.innerHTML = `
                        <h3>✅ Registration Successful!</h3>
                        <p>Save these credentials securely. You won't be able to see them again!</p>
                        <div class="credential">
                            <strong>App ID:</strong>
                            ${data.data.app_id}
                        </div>
                        <div class="credential">
                            <strong>API Key:</strong>
                            ${data.data.api_key}
                        </div>
                        <div class="credential">
                            <strong>HMAC Secret:</strong>
                            ${data.data.hmac_secret}
                        </div>
                        <div class="credential">
                            <strong>Webhook URL:</strong>
                            ${data.data.webhook_url}
                        </div>
                    `;
                    form.reset();
                } else {
                    resultDiv.className = 'result error';
                    const errorMsg = data.detail?.message || data.detail || data.message || 'Registration failed';
                    resultDiv.innerHTML = `
                        <h3>❌ Registration Failed</h3>
                        <p>${errorMsg}</p>
                    `;
                }
            } catch (error) {
                resultDiv.className = 'result error';
                resultDiv.innerHTML = `
                    <h3>❌ Network Error</h3>
                    <p>Failed to connect to the server. Please try again.</p>
                `;
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerHTML = 'Register';
                resultDiv.style.display = 'block';
            }
        });
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)


@router.post("/register", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def register_client(
    request: ClientRegisterRequest,
    db: Session = Depends(get_db)
):
    """Register a new client and generate credentials"""
    
    try:
        # Check if email already exists
        existing_client = db.query(Client).filter(Client.email == request.email).first()
        if existing_client:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "EMAIL_EXISTS",
                    "message": "Email already registered"
                }
            )
        
        # Generate credentials
        app_id, api_key, hmac_secret = generate_credentials()
        
        # Hash password - passlib will handle the password properly
        # For long passwords, truncate to reasonable length first (72 characters is safe)
        password_to_hash = request.password[:72] if len(request.password) > 72 else request.password
        password_hash = pwd_context.hash(password_to_hash)
        
        # Create new client
        new_client = Client(
            app_id=app_id,
            organization_name=request.organization_name,
            email=request.email,
            api_key=api_key,
            hmac_secret=hmac_secret,
            webhook_url=str(request.webhook_url),
            password_hash=password_hash,
            status='active'
        )
        
        db.add(new_client)
        db.commit()
        db.refresh(new_client)
        
        logger.info(f"New client registered: {app_id}")
        
        # Prepare response
        response_data = ClientRegisterResponse(
            app_id=new_client.app_id,
            api_key=new_client.api_key,
            hmac_secret=new_client.hmac_secret,
            webhook_url=new_client.webhook_url,
            created_at=new_client.created_at
        )
        
        return APIResponse(
            success=True,
            data=response_data.dict(),
            message="Client registered successfully"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering client: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Failed to register client"
            }
        )

