# 🍜 Foodiebay — Online Food Ordering (Swiggy-style)

A full-stack food delivery web app + Android APK inspired by **Swiggy**: browse restaurants,
build a cart, pay via **UPI (direct to merchant) or Razorpay**, and track your order live.

| Layer | Tech | Deploy target |
|---|---|---|
| **Backend API** | Django 6.1 · DRF · SimpleJWT · **Supabase PostgreSQL** | **Render** |
| **Frontend web** | React 19 · Vite 7 · TypeScript | **Firebase Hosting** |
| **Android app** | Same React app wrapped via **Capacitor 7** | Local APK build |
| **Payments** | **Direct UPI (QR + intent link)** · Razorpay (optional) | — |

---

## ✨ Features

- 🏪 **Restaurant discovery** — search, Pure-Veg / Open-now filters, sort by rating or delivery time
- 📖 **Menus** with categories, veg/non-veg markers, bestsellers, availability
- 🛒 **Cart** — persists in localStorage, auto-switches when you change restaurants
- 💸 **UPI payments** — after checkout a QR + "Open UPI App" button pays directly to the
  merchant VPA (`7780383832@upi`). Works in every UPI app (GPay · PhonePe · Paytm)
- 🧾 **Razorpay (optional)** — when `RAZORPAY_KEY_ID`/`RAZORPAY_KEY_SECRET` are set, the
  professional Razorpay Checkout opens instead (cards/netbanking/UPI), with server-side
  HMAC signature verification + webhook (`payment.captured`)
- 🛡️ **Server-side billing** — item prices/taxes/fees always recomputed on the backend
- 🔐 **Email auth** — JWT access + refresh, auto-refresh, case-insensitive login
- 🛵 **Live order tracking** — placed → preparing → out-for-delivery → delivered with polling
- 📱 **Android APK** — the same web app, packaged with Capacitor
- 🌱 **Seed data** — 10 Swiggy-style restaurants with full menus (`python manage.py seed_data`)

### Demo accounts
| Role | Email | Password |
|---|---|---|
| Admin (Django admin) | `admin@foodiebay.app` | `admin123` |
| Customer | `demo@foodiebay.app` | `demo1234` |

### Database
The app uses **Supabase PostgreSQL** (set in `backend/.env`):
```
DATABASE_URL=postgresql://postgres:Supabase%40123@db.ndimnbxuteqcuzsyocht.supabase.co:5432/postgres?sslmode=require
```
> Note: the `@` inside the password must be URL-encoded as `%40` in the connection string.

---

## 🚀 Run locally

**Backend** (http://127.0.0.1:8000)
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate            # Windows (use source .venv/bin/activate on macOS/Linux)
pip install -r requirements.txt
copy .env.example .env             # edit if your DB/keys differ
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

**Frontend** (http://127.0.0.1:5173) — Vite proxies `/api` → `:8000`
```bash
cd frontend
npm install
npm run dev
```

**Payments:** with no Razorpay keys configured, checkout shows a **UPI QR + intent link**
paying straight to `7780383832@upi` — fully testable without any gateway account.
Add Razorpay keys (from [dashboard](https://dashboard.razorpay.com/app/keys)) to switch to
Razorpay Checkout.

---

## ☁️ Deploy to Render (backend)

1. Push this repo to GitHub.
2. [Render dashboard](https://dashboard.render.com) → **New → Blueprint** → pick the repo.
   `render.yaml` defines the `foodiebay-api` web service.
3. Fill in the prompted env vars:
   - `DATABASE_URL` → your Supabase URL (password `@` encoded as `%40`, see above)
   - `CORS_ALLOWED_ORIGINS` → your Firebase URL, e.g. `https://<project>.web.app`
   - `RAZORPAY_KEY_ID` / `RAZORPAY_KEY_SECRET` → optional, for Razorpay Checkout
   - `RAZORPAY_WEBHOOK_SECRET` → Settings → Webhooks, point at
     `https://<your-render-app>.onrender.com/api/v1/payments/webhook/` (event: `payment.captured`)
   - `UPI_VPA` / `UPI_PAYEE_NAME` → default to `7780383832@upi` / `Foodiebay`
4. Your API will be live at `https://foodiebay-api.onrender.com` (health: `/api/v1/health/`).

---

## 🔥 Deploy to Firebase Hosting (frontend web)

1. `npm install -g firebase-tools && firebase login`
2. `firebase use --add` inside `frontend/` → select your project, alias `default`
3. Create `frontend/.env.production`:
   ```
   VITE_API_BASE_URL=https://foodiebay-api.onrender.com
   ```
4. Build + deploy:
   ```bash
   cd frontend
   npm run build
   firebase deploy
   ```
5. Add your Firebase URL to the backend's `CORS_ALLOWED_ORIGINS` on Render.

---

## 🤖 Build the Android APK

The same React app is packaged natively with Capacitor (project in `frontend/android`).

1. Point the app at your live API — `frontend/.env.production`:
   ```
   VITE_API_BASE_URL=https://foodiebay-api.onrender.com
   ```
2. Rebuild the web bundle and sync it into the Android project:
   ```bash
   cd frontend
   npm run android:sync        # = npm run build && npx cap sync android
   ```
3. Build the APK:
   - **Android Studio:** `npm run android:open` → *Build → Build App Bundle(s)/APK(s) → Build APK(s)*
   - **CLI** (JDK 17–21 + Android SDK 35+):
     ```bash
     cd android
     gradlew assembleDebug                 # debug APK
     gradlew assembleRelease               # needs signing config (see below)
     ```
   The debug APK lands in `android/app/build/outputs/apk/debug/app-debug.apk`.

4. **Release signing** — create a keystore once and reference it in
   `android/app/build.gradle` (`signingConfigs.release`):
   ```
   keytool -genkey -v -keystore foodiebay.keystore -alias foodiebay -keyalg RSA -keysize 2048 -validity 10000
   ```

> UPI intent links (`upi://pay?...`) open installed UPI apps directly from the APK —
> the ideal payment UX on Android in India.

---

## 🗂 Repo layout

```
├── render.yaml                  # Render blueprint (API service, uses Supabase DB)
├── backend/
│   ├── config/                  # Django settings/urls/wsgi (+ .env loader)
│   ├── core/                    # health + API index
│   ├── accounts/                # email auth (register/login/JWT/me)
│   ├── restaurants/             # restaurants, menus, seed_data command
│   └── orders/                  # orders, Razorpay + UPI, webhook
└── frontend/
    ├── src/                     # React app (pages, contexts, components)
    ├── android/                 # Capacitor Android project (APK)
    ├── firebase.json            # Firebase Hosting config
    └── capacitor.config.ts
```

## 🔌 API overview (`/api/v1`)

| Endpoint | Method | What |
|---|---|---|
| `/health/` | GET | Liveness probe |
| `/restaurants/` | GET | List + filters (`search`, `veg`, `open`, `sort`) |
| `/restaurants/{id}/` | GET | Menu with categories |
| `/auth/register/` | POST | Create account |
| `/auth/token/` | POST | Login (JWT) |
| `/auth/me/` | GET | Current user |
| `/orders/checkout/` | POST | Create order + UPI intent + Razorpay order |
| `/orders/verify-payment/` | POST | Confirm payment (Razorpay signature or UPI) |
| `/orders/` | GET | My orders |
| `/orders/{id}/` | GET | Order detail |
| `/orders/{id}/advance/` | POST | Demo: progress status |
| `/orders/{id}/cancel/` | POST | Cancel order |
| `/payments/webhook/` | POST | Razorpay webhook |
