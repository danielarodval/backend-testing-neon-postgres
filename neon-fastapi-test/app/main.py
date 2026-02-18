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
    if not signature:
        return False

    # The signature from GitHub starts with 'sha256='
    if not signature.startswith("sha256="):
        return False

    # Remove the 'sha256=' prefix
    signature = signature[7:]

    # Retrieve the webhook secret from settings (Pydantic field is WEBHOOK_SECRET)
    secret_value = getattr(settings, "WEBHOOK_SECRET", None)
    if not secret_value:
        return False

    # Calculate the HMAC SHA256 signature using our webhook secret
    secret = secret_value.encode()
    expected_signature = hmac.new(secret, body, hashlib.sha256).hexdigest()

    # Compare the calculated signature with the one from GitHub
    return hmac.compare_digest(expected_signature, signature)

async def process_webhook_event(event_id, db):
    # Fetch the webhook event from the database
    result = await db.execute(select(WebhookEvent).where(WebhookEvent.id == event_id))
    event = result.scalars().first()

    if not event:
        return

    try:
        # Process different event types
        if event.event_type == "push":
            await process_push_event(event)
        elif event.event_type == "pull_request":
            await process_pull_request_event(event)
        elif event.event_type == "issues":
            await process_issue_event(event)
        # Add more event types as needed

        # Mark the event as processed
        event.processed = True
        await db.commit()

    except Exception as e:
        print(f"Error processing webhook event {event_id}: {e}")

async def process_push_event(event):
    """Process a GitHub push event."""
    payload = event.payload
    repo_name = payload.get("repository", {}).get("full_name")
    ref = payload.get("ref")
    commits = payload.get("commits", [])

    print(f"Push to {repo_name} on {ref} with {len(commits)} commits")
    # Handle the push event based on the commits

async def process_pull_request_event(event):
    """Process a GitHub pull request event."""
    payload = event.payload
    action = payload.get("action")
    pr_number = payload.get("number")
    repo_name = payload.get("repository", {}).get("full_name")

    print(f"Pull request #{pr_number} {action} in {repo_name}")
    # Handle the pull request based on the action (opened, closed, etc.)

async def process_issue_event(event):
    """Process a GitHub issue event."""
    payload = event.payload
    action = payload.get("action")
    issue_number = payload.get("issue", {}).get("number")
    repo_name = payload.get("repository", {}).get("full_name")

    print(f"Issue #{issue_number} {action} in {repo_name}")
    # Handle the issue based on the action (opened, closed, etc.)