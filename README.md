## VaultChat (Django + HTMX + Postgres/pgvector)

VaultChat is a secure, multi-tenant “chat over your PDFs” MVP:
- Django server-rendered UI + HTMX streaming chat
- Postgres + pgvector for RAG
- Celery + Redis for background PDF ingestion
- Stripe Checkout (one-time pilot fee) + webhook to unlock an Organization

## Features
- **Multi-tenant isolation**: every data object is organization-scoped
- **Documents**: upload PDFs, ingest in background, status tracking
- **RAG chat**: retrieval + streaming responses
- **Pilot automation**: org creation → intake → paywall → Stripe Checkout → webhook unlock
- **Audit events**: basic event trail for key actions

## Prereqs
- Docker Desktop
- (Optional) Stripe CLI for local webhook forwarding

## Local setup
### 1) Configure environment
Copy the template and fill required values:

```bash
cp .env.example .env
```

Required for RAG + chat:
- `OPENAI_API_KEY=...`

Required for Stripe pilot flow:
- `STRIPE_SECRET_KEY=...`
- `STRIPE_PILOT_PRICE_ID=price_...`
- `STRIPE_WEBHOOK_SECRET=whsec_...` (use Stripe CLI locally; see below)

### 2) Start services

```bash
docker compose up --build
```

### 3) Run migrations + create a superuser

```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

## Live preview (local)
Open these URLs:
- App: `http://localhost:8000/`
- Dashboard: `http://localhost:8000/dashboard/`
- Admin: `http://localhost:8000/admin/`

Recommended “sales demo” clickthrough:
1. Go to `/` and click **Start your pilot**
2. Sign in
3. Create an organization (`/org/create/`)
4. Fill pilot intake (`/pilot/intake/`)
5. Go to paywall (`/billing/pay/`) and start Stripe Checkout
6. After payment + webhook: go to onboarding (`/onboarding/`)
7. Upload a PDF (`/documents/`) and wait until it becomes **Ready**
8. Ask questions in chat (`/chat/`)

## Stripe (local webhook)
For step-by-step setup (Dashboard + CLI), see:
- `docs/stripe_setup.md`

Quick local webhook forwarding example:

```bash
stripe login
stripe listen --forward-to localhost:8000/billing/webhook/
```

Copy the printed `whsec_...` into `.env` as `STRIPE_WEBHOOK_SECRET`, then restart:

```bash
docker compose restart web
```

## Useful commands
- Rebuild containers after dependency changes:

```bash
docker compose build web worker
docker compose up -d
```

- Tail logs:

```bash
docker compose logs -f web
docker compose logs -f worker
```

## Production notes (high level)
To deploy production you’ll typically want:
- Managed Postgres + Redis
- Object storage for uploads (S3/R2) instead of local volumes
- Gunicorn behind a reverse proxy (TLS)
- `DEBUG=0`, secure cookies/headers, real domain in `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS`
- Stripe webhook configured to `https://<your-domain>/billing/webhook/`

### Production compose (reference)
This repo includes a minimal production compose file:
- `docker-compose.prod.yml`

It assumes you provide `DATABASE_URL`, `REDIS_URL`, and all secrets via your platform (not via mounted `.env`), and that you run:

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

Then run:

```bash
docker compose -f docker-compose.prod.yml exec web python manage.py migrate
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

