## Stripe setup (Pilot one-time fee)

This app uses **Stripe Checkout** (hosted) and a **server-side webhook** to unlock an Organization after payment.

### 1) Create product + one-time price (Stripe Dashboard)
1. Open Stripe Dashboard → switch to **Test mode**.
2. Go to **Products** → **Add product**.
3. Name: `Secure AI Wrapper Pilot`.
4. Pricing:
   - Type: **One-time**
   - Currency: EUR (or your currency)
   - Amount: your pilot fee (e.g. 2500.00)
5. Save.
6. Copy the **Price ID** (looks like `price_...`).

Set it in your `.env`:
- `STRIPE_PILOT_PRICE_ID=price_...`

### 2) Get your secret API key
1. Dashboard → **Developers** → **API keys**
2. Copy **Secret key** (test key starts with `sk_test_...`)

Set:
- `STRIPE_SECRET_KEY=sk_test_...`

### 3) Configure webhook (production)
In production you will create a webhook endpoint that points to:
- `https://<your-domain>/billing/webhook/`

Listen for event:
- `checkout.session.completed`

Copy the **Signing secret** (`whsec_...`) into:
- `STRIPE_WEBHOOK_SECRET=whsec_...`

### 4) Local webhook testing (recommended: Stripe CLI)
Install Stripe CLI, then:
1. Login:
```bash
stripe login
```
2. Forward webhooks to your local Django server:
```bash
stripe listen --forward-to localhost:8000/billing/webhook/
```
3. Copy the printed signing secret (`whsec_...`) into `.env` as `STRIPE_WEBHOOK_SECRET`.

4. Trigger a test event:
```bash
stripe trigger checkout.session.completed
```
Note: for a full end-to-end test with your actual Checkout session, keep `stripe listen` running and complete the Checkout flow in your browser.

### 5) Success/cancel URLs
Defaults are already in `.env.example`:
- `STRIPE_SUCCESS_URL=http://localhost:8000/billing/success/`
- `STRIPE_CANCEL_URL=http://localhost:8000/billing/cancel/`

In production, set them to your real domain.

### 6) How unlocking works (important)
The app does **not** unlock based on the browser redirect.\n+
It unlocks only when Stripe sends `checkout.session.completed` to `/billing/webhook/`.

