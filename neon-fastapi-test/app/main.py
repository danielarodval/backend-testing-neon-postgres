import json
import hmac
import hashlib
from fastapi import FastAPI, Request, HTTPException, Depends, Header, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db, engine, Base
from app.models import WebhookEvent
from app.config import settings

# Initialize the FastAPI app
app = FastAPI(title="Neon FastAPI Webhook Receiver")

# Create database tables on startup
@app.on_event("startup")
async def startup():
    # Create database tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Helper function to verify webhook signature
@app.get("/")
async def root():
    return {"message": "Welcome to the Neon FastAPI Webhook Receiver!"}

# Endpoint to receive webhooks
@app.get("/webhooks/events")
async def view_webhook_events(limit: int = 10, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(WebhookEvent).order_by(WebhookEvent.created_at.desc()).limit(limit))
    events = result.scalars().all()
    return events

@app.post("/webhooks/github")
async def github_webhook(
    request: Request,
    x_github_event: str = Header(None),
    x_github_delivery: str = Header(None),
    x_hub_signature_256: str = Header(None),
    db: AsyncSession = Depends(get_db)
):
    # Read the raw request body
    body = await request.body()

    # Verify the signature using the WEBHOOK_SECRET from settings
    is_valid = verify_signature(body, x_hub_signature_256)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid signature"
        )
    
    # Parse the JSON payload
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload"
        )
    
    # Store the webhook event in the database
    webhook_event = WebhookEvent(
        event_type=x_github_event,
        delivery_id=x_github_delivery,
        signature=x_hub_signature_256,
        payload=payload,
        processed=False
    )

    # Add the event to the database session and commit
    db.add(webhook_event)
    await db.commit()
    await db.refresh(webhook_event)

    # Process the webhook event (you can implement your processing logic here)
    await process_webhook_event(webhook_event.id, db)

    return {"status": "success", "event_id": webhook_event.id}

def verify_signature(body, signature):
    secret = settings.WEBHOOK_SECRET.encode()
    computed_signature = 'sha256=' + hmac.new(secret, body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(computed_signature, signature)

async def process_webhook_event(event_id, db):
    # Fetch the event from the database
    result = await db.execute(select(WebhookEvent).where(WebhookEvent.id == event_id))
    event = result.scalar_one_or_none()

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook event not found"
        )
    
    # Implement your processing logic here (e.g., trigger CI/CD, send notifications, etc.)
    print(f"Processing webhook event: {event}")

    # Mark the event as processed
    event.processed = True
    await db.commit()
    