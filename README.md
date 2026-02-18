# Backend Testing with Neon Postgres

## Description

Testing the deployment of a Neon Postgres backend with FastAPI webhooks to log data from a local server via a Tailscale proxy. Containerized using Docker to package Postgres and Fast API.

## Demo

Add a GIF, image, or link to a live demo. Visuals grab attention.

## Deployment Process

- [Singular Neon Postgres Database](./neon-solo-test)
    - Iterated through the tutorial on the Neon documentation to test the creation and understand the various sub-component scripts and requirements needed to rollout a table and update items on the online version of Neon Postgres. 
    - In doing so there are a slew of limitations found based around resources and free subscription limitations.
        - As such in the next stage/iteration with integrating Fast API I will begin doing research tangentially on docker container instances for a local implementation of Neon Postgres rather than relying on the cloud based implementation.
- [Testing Neon Postgres with Fast API](./neon-fastapi-test)
    - Commenced with the creation of the database models still leveraging the cloud instance for testing, namely focused on FastAPI and Neon interoperability.
    - Built using the webhooks guide that Neon has on their site, it was created specifically centered around GitHub webhooks with an ngrok exposed proxy layer, though in testing, I used the standard FastAPI interface, and forced calls via the test cases.

- [Drafting the Actual Deployment](./actual-use-case)
    - description

## Usage

Show how to run it or use it. Include example commands or screenshots.

## Neon setup (what was done)

- Neon organization: `org-lingering-night-08521348`
- Neon project used for testing: `still-block-95385845`
- A Neon Postgres connection string was retrieved and stored locally in the service `.env` files (do not commit secrets).

Key files updated to integrate Neon and webhook testing:

- [neon-fastapi-test/app/database.py](neon-fastapi-test/app/database.py) — builds the async engine from `DATABASE_URL`, avoids inserting a literal `None` port when absent, and passes SSL via `connect_args`.
- [neon-fastapi-test/app/main.py](neon-fastapi-test/app/main.py) — webhook receiver: safely reads `WEBHOOK_SECRET` from settings, verifies GitHub `X-Hub-Signature-256`, and persists `WebhookEvent` rows.
- [neon-solo-test/delete_data.py](neon-solo-test/delete_data.py) — added validation for `CONNECTION_STRING` env var and clearer error if missing.

## Local run & test (FastAPI webhook receiver)

1. Create and activate your virtual environment and install requirements (see each folder's `requirements.txt`).

2. Add a `.env` in `neon-fastapi-test/` with:

```
DATABASE_URL=<your Neon DATABASE_URL goes here>
WEBHOOK_SECRET=<your webhook secret>
```

3. Start the app:

```bash
cd neon-fastapi-test
source .venv/bin/activate
uvicorn app.main:app --reload
```

4. Open the interactive docs at: `http://127.0.0.1:8000/docs` to inspect endpoints and use Try It Out.

5. Example curl test — the signature must be computed over the exact request body bytes using your `WEBHOOK_SECRET`:

```bash
payload='{"repository":{"full_name":"me/repo"},"ref":"refs/heads/main","commits":[] }'
sig=$(printf '%s' "$payload" | openssl dgst -sha256 -hmac "$WEBHOOK_SECRET" -binary | xxd -p -c 256)
curl -X POST 'http://127.0.0.1:8000/webhooks/github' \
    -H 'Content-Type: application/json' \
    -H "X-GitHub-Event: push" \
    -H "X-GitHub-Delivery: test-delivery" \
    -H "X-Hub-Signature-256: sha256=$sig" \
    -d "$payload"
```

6. Verify persisted events with:

```bash
curl http://127.0.0.1:8000/webhooks/events
```

## Notes & recommendations

- Never commit `.env` files with secrets or the full Neon connection string to version control.
- If you need easier local testing, consider adding a development-only bypass (for example an `X-DEV-BYPASS` header that short-circuits signature validation) guarded by a config flag — do not enable this in production.
- The Neon connection string was used with SQLAlchemy async engine (`asyncpg`) — SSL is passed via `connect_args` rather than query params to avoid `asyncpg` errors.


## Features

List key features so users know what to expect.

## Built With

Mention the languages, frameworks, and tools you used.

## License

Let people know how they can use or reuse your code.

## Credits / Acknowledgments (optional)

- [Markdown Guidelines Help](https://medium.com/@fulton_shaun/readme-rules-structure-style-and-pro-tips-faea5eb5d252)
- 