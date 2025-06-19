import os
from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.responses import StreamingResponse, Response
from pydantic import BaseModel, HttpUrl, EmailStr
import uvicorn
import asyncio
from scan import run_scan
from rule_engine import load_rules, evaluate_rules
import json
from typing import List, Optional
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from models import User, Organisation, Role, get_db, SessionLocal, ApiKey
from sqlalchemy.orm import Session
import secrets
import hashlib
import stripe
from sqlalchemy.exc import SQLAlchemyError
import stripe.error
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from audit import log_audit
from fastapi import Header
from fastapi.responses import JSONResponse
from integrations import NotificationManager, test_slack_webhook, test_resend_api_key
import logging
from fastapi.openapi.utils import get_openapi

logger = logging.getLogger(__name__)

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = data.copy()
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(lambda request: request.headers.get('Authorization', '').replace('Bearer ', '')), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        user_id = int(user_id)
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_user_or_apikey(request: Request, db: Session = Depends(get_db)):
    # Prefer JWT if both are present
    auth_header = request.headers.get('Authorization', '')
    api_key_header = request.headers.get('x-api-key', '')
    if auth_header.startswith('Bearer '):
        token = auth_header.replace('Bearer ', '')
        return get_current_user(token, db)
    elif api_key_header:
        key_hash = hashlib.sha256(api_key_header.encode()).hexdigest()
        api_key_obj = db.query(ApiKey).filter(ApiKey.key_hash == key_hash, ApiKey.is_active == True).first()
        if not api_key_obj:
            raise HTTPException(status_code=401, detail="Invalid or inactive API key")
        user = db.query(User).filter(User.id == api_key_obj.user_id).first()
        if not user or not user.is_active == True:  # type: ignore
            raise HTTPException(status_code=401, detail="User not found or inactive for API key")
        return user
    else:
        raise HTTPException(status_code=401, detail="Missing Authorization or x-api-key header")

def auth_required(role_name: str):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            request = kwargs.get('request') or (args[0] if args and isinstance(args[0], Request) else None)
            if request is None or not isinstance(request, Request):
                raise ValueError("Request object is required for authentication")
            db = next(get_db())
            user = get_current_user_or_apikey(request, db)
            if not any(role.name == role_name for role in user.roles):
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            kwargs['current_user'] = user
            return await func(*args, **kwargs)
        return wrapper
    return decorator

app = FastAPI(
    title="RegulaAI Scanner",
    description="API for scanning websites for GDPR compliance",
    version="0.1.0",
    tags=[
        {"name": "Auth", "description": "Authentication and user management endpoints"},
        {"name": "Scans", "description": "Website scanning and compliance checking endpoints"},
        {"name": "Billing", "description": "Billing and subscription management endpoints"},
        {"name": "Integrations", "description": "Slack and email integration endpoints"},
        {"name": "Settings", "description": "API key and settings management endpoints"},
        {"name": "Monitoring", "description": "Metrics and monitoring endpoints"}
    ]
)

# Prometheus metrics
scan_duration_seconds = Histogram('scan_duration_seconds', 'Scan duration in seconds')
violations_total = Counter('violations_total', 'Total violations by severity', ['severity'])
badge_requests_total = Counter('badge_requests_total', 'Total badge requests')

# Assign weights to severities
SEVERITY_WEIGHTS = {
    "critical": 50,
    "high": 30,
    "medium": 15,
    "low": 5
}

def get_rule_weight(severity: str) -> int:
    return SEVERITY_WEIGHTS.get(severity, 10)

class ScanRequest(BaseModel):
    url: HttpUrl
    persona: Optional[str] = None

class BatchScanRequest(BaseModel):
    scans: List[ScanRequest]

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    organisation_name: str
    organisation_domain: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ApiKeyCreateRequest(BaseModel):
    name: str

class CheckoutSessionRequest(BaseModel):
    success_url: str
    cancel_url: str

# Stripe config
PRO_PLAN_PRICE_ID = os.getenv("STRIPE_PRO_PLAN_PRICE_ID", "price_123")
PRO_PLAN_SCANS_PER_MONTH = int(os.getenv("PRO_PLAN_SCANS_PER_MONTH", "10000"))
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_123")

@app.post("/auth/register", tags=["Auth"])
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == request.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    org = Organisation(name=request.organisation_name, domain=request.organisation_domain)
    db.add(org)
    db.commit()
    db.refresh(org)
    user = User(
        email=request.email,
        password_hash=get_password_hash(request.password),
        first_name=request.first_name,
        last_name=request.last_name,
        organisation_id=org.id,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    # Assign 'owner' role
    owner_role = db.query(Role).filter(Role.name == 'owner').first()
    if not owner_role:
        owner_role = Role(name='owner', description='Organisation owner')
        db.add(owner_role)
        db.commit()
        db.refresh(owner_role)
    user.roles.append(owner_role)
    db.commit()
    return {"msg": "User and organisation registered successfully"}

@app.post("/auth/login", tags=["Auth"])
def login(request: Request, body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not user.is_active == True:  # type: ignore
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token({"sub": user.id})
    refresh_token = create_refresh_token({"sub": user.id})
    log_audit(
        event="login",
        user_id=user.id,  # type: ignore[arg-type]
        meta={"email": body.email},
        ip=request.client.host if request and request.client else None
    )
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@app.post("/scan", tags=["Scans"])
@auth_required("viewer")
async def scan_endpoint(request: ScanRequest, current_user: User = Depends(get_current_user_or_apikey), db: Session = Depends(get_db), raw_request: Request = Depends()):
    # Enforce quota
    org = db.query(Organisation).filter(Organisation.id == current_user.organisation_id).with_for_update().first()
    if not org:
        raise HTTPException(status_code=404, detail="Organisation not found")
    if org.remaining_scans_month <= 0:  # type: ignore[operator]
        raise HTTPException(status_code=402, detail="Scan quota exceeded. Please upgrade your plan or wait for reset.")
    try:
        org.remaining_scans_month -= 1  # type: ignore[assignment]
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update scan quota.")
    try:
        with scan_duration_seconds.time():
            scan_result = await run_scan(str(request.url), persona_id=request.persona)
        rules = load_rules()
        violations = evaluate_rules(scan_result, rules)
        for v in violations:
            violations_total.labels(severity=v['severity']).inc()
        total_weight = sum(get_rule_weight(v['severity']) for v in violations)
        score = max(0, 100 - total_weight)
        response = scan_result.copy()
        response["score"] = score
        response["violations"] = violations
        
        # Check for high-severity violations and send notifications
        high_severity_violations = [
            v for v in violations 
            if v.get('severity', '').lower() in ['high', 'critical']
        ]
        
        if high_severity_violations:
            # Send notifications asynchronously (don't block the response)
            try:
                notification_manager = NotificationManager(org)
                domain = str(request.url).replace('https://', '').replace('http://', '').split('/')[0]
                notification_manager.send_high_severity_alert(domain, score, violations)
            except Exception as e:
                # Log notification errors but don't fail the scan
                logger.error(f"Failed to send notifications: {str(e)}")
        
        log_audit(
            event="scan",
            user_id=current_user.id,  # type: ignore[arg-type]
            meta={"url": request.url, "result": response},
            ip=raw_request.client.host if raw_request and raw_request.client else None
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/batch_scan", tags=["Scans"])
@auth_required("viewer")
async def batch_scan_endpoint(request: BatchScanRequest, current_user: User = Depends(get_current_user_or_apikey)):
    async def scan_and_serialize(scan_req: ScanRequest):
        try:
            with scan_duration_seconds.time():
                scan_result = await run_scan(str(scan_req.url), persona_id=scan_req.persona)
            rules = load_rules()
            violations = evaluate_rules(scan_result, rules)
            for v in violations:
                violations_total.labels(severity=v['severity']).inc()
            total_weight = sum(get_rule_weight(v['severity']) for v in violations)
            score = max(0, 100 - total_weight)
            response = scan_result.copy()
            response["score"] = score
            response["violations"] = violations
            return json.dumps(response)
        except Exception as e:
            return json.dumps({"url": str(scan_req.url), "error": str(e)})

    async def ndjson_stream():
        coros = [scan_and_serialize(scan_req) for scan_req in request.scans]
        for fut in asyncio.as_completed(coros):
            result = await fut
            yield result + "\n"

    return StreamingResponse(ndjson_stream(), media_type="application/x-ndjson")

@app.get("/metrics", tags=["Monitoring"])
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Example badge endpoint for badge_requests_total
@app.get("/badge/{site_id}", tags=["Monitoring"])
def badge(site_id: str):
    badge_requests_total.inc()
    # ... badge generation logic ...
    return Response("<svg><!-- badge --></svg>", media_type="image/svg+xml")

@app.post("/settings/api-keys", tags=["Settings"])
@auth_required("owner")
def create_api_key(request: ApiKeyCreateRequest, current_user: User = Depends(get_current_user_or_apikey), db: Session = Depends(get_db), raw_request: Request = Depends()):
    # Generate a secure 40-char token
    api_key = secrets.token_urlsafe(30)[:40]
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    # Store in DB
    api_key_obj = ApiKey(
        name=request.name,
        key_hash=key_hash,
        user_id=current_user.id,
        is_active=True
    )
    db.add(api_key_obj)
    db.commit()
    db.refresh(api_key_obj)
    log_audit(
        event="create_api_key",
        user_id=current_user.id,  # type: ignore[arg-type]
        meta={"api_key_id": api_key_obj.id, "name": request.name},
        ip=raw_request.client.host if raw_request and raw_request.client else None
    )
    return {"api_key": api_key, "id": api_key_obj.id}

@app.post("/billing/create-checkout-session", tags=["Billing"])
@auth_required("owner")
def create_checkout_session(request: CheckoutSessionRequest, current_user: User = Depends(get_current_user_or_apikey), db: Session = Depends(get_db)):
    org = db.query(Organisation).filter(Organisation.id == current_user.organisation_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organisation not found")
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="subscription",
            line_items=[{
                "price": PRO_PLAN_PRICE_ID,
                "quantity": 1,
            }],
            customer_email=str(current_user.email),
            metadata={"organisation_id": str(org.id)},
            success_url=request.success_url,
            cancel_url=request.cancel_url,
        )
        return {"checkout_url": session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/billing/webhook", tags=["Billing"])
async def stripe_webhook(request: Request, stripe_signature: str = Header(None), db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = stripe_signature or request.headers.get("stripe-signature")
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return JSONResponse(status_code=400, content={"error": "Invalid payload"})
    except stripe.error.SignatureVerificationError:  # type: ignore[attr-defined]
        return JSONResponse(status_code=400, content={"error": "Invalid signature"})

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        org_id = session["metadata"].get("organisation_id")
        if org_id:
            org = db.query(Organisation).filter(Organisation.id == int(org_id)).first()
            if org:
                org.plan = 'PRO'  # type: ignore[assignment]
                org.remaining_scans_month = PRO_PLAN_SCANS_PER_MONTH  # type: ignore[assignment]
                db.commit()
    return {"status": "success"}

# Integration endpoints
class SlackWebhookRequest(BaseModel):
    webhook_url: str

class EmailSettingsRequest(BaseModel):
    resend_api_key: str
    notification_email: str

class TestIntegrationRequest(BaseModel):
    test_email: str

@app.post("/integrations/slack", tags=["Integrations"])
@auth_required("owner")
def configure_slack_webhook(request: SlackWebhookRequest, current_user: User = Depends(get_current_user_or_apikey), db: Session = Depends(get_db), raw_request: Request = Depends()):
    """Configure Slack webhook URL for high-severity violation alerts."""
    org = db.query(Organisation).filter(Organisation.id == current_user.organisation_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organisation not found")
    
    # Test the webhook URL
    if not test_slack_webhook(request.webhook_url):
        raise HTTPException(status_code=400, detail="Invalid Slack webhook URL. Please check the URL and try again.")
    
    # Update the organisation
    org.slack_webhook_url = request.webhook_url  # type: ignore[assignment]
    db.commit()
    
    log_audit(
        event="configure_slack_webhook",
        user_id=current_user.id,  # type: ignore[arg-type]
        meta={"webhook_url": request.webhook_url},
        ip=raw_request.client.host if raw_request and raw_request.client else None
    )
    
    return {"message": "Slack webhook configured successfully"}

@app.post("/integrations/email", tags=["Integrations"])
@auth_required("owner")
def configure_email_settings(request: EmailSettingsRequest, current_user: User = Depends(get_current_user_or_apikey), db: Session = Depends(get_db), raw_request: Request = Depends()):
    """Configure email settings for high-severity violation alerts."""
    org = db.query(Organisation).filter(Organisation.id == current_user.organisation_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organisation not found")
    
    # Test the Resend API key
    if not test_resend_api_key(request.resend_api_key, request.notification_email):
        raise HTTPException(status_code=400, detail="Invalid Resend API key or email address. Please check your credentials and try again.")
    
    # Update the organisation
    org.resend_api_key = request.resend_api_key  # type: ignore[assignment]
    org.notification_email = request.notification_email  # type: ignore[assignment]
    db.commit()
    
    log_audit(
        event="configure_email_settings",
        user_id=current_user.id,  # type: ignore[arg-type]
        meta={"notification_email": request.notification_email},
        ip=raw_request.client.host if raw_request and raw_request.client else None
    )
    
    return {"message": "Email settings configured successfully"}

@app.post("/integrations/test-email", tags=["Integrations"])
@auth_required("owner")
def test_email_integration(request: TestIntegrationRequest, current_user: User = Depends(get_current_user_or_apikey), db: Session = Depends(get_db)):
    """Test email integration by sending a test email."""
    org = db.query(Organisation).filter(Organisation.id == current_user.organisation_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organisation not found")
    
    if not org.resend_api_key:  # type: ignore[truthy-function]
        raise HTTPException(status_code=400, detail="Email integration not configured. Please configure email settings first.")
    
    # Test the email integration
    if test_resend_api_key(org.resend_api_key, request.test_email):  # type: ignore[arg-type]
        return {"message": "Test email sent successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to send test email. Please check your configuration.")

@app.get("/integrations/status", tags=["Integrations"])
@auth_required("owner")
def get_integration_status(current_user: User = Depends(get_current_user_or_apikey), db: Session = Depends(get_db)):
    """Get the current integration status for the organisation."""
    org = db.query(Organisation).filter(Organisation.id == current_user.organisation_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organisation not found")
    
    return {
        "slack_configured": bool(org.slack_webhook_url),  # type: ignore[arg-type]
        "email_configured": bool(org.resend_api_key and org.notification_email),  # type: ignore[arg-type]
        "notification_email": org.notification_email  # type: ignore[return-value]
    }

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        response.headers['Strict-Transport-Security'] = 'max-age=63072000; includeSubDomains; preload'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response

app.add_middleware(SecurityHeadersMiddleware)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="RegulaAI Scanner API",
        version="0.1.0",
        description="Complete API for scanning websites for GDPR compliance with authentication, billing, and integrations",
        routes=app.routes,
    )
    
    # Add custom info
    openapi_schema["info"]["contact"] = {
        "name": "RegulaAI Support",
        "email": "support@regulaai.com",
        "url": "https://regulaai.com"
    }
    
    # Add servers
    openapi_schema["servers"] = [
        {
            "url": "http://localhost:8000",
            "description": "Local development server"
        },
        {
            "url": "https://api.regulaai.com",
            "description": "Production server"
        }
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 