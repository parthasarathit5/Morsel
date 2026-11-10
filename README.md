# 🍜 FoodFlow — Online Food Ordering (Swiggy-style)

A full-stack food delivery web app + Android APK inspired by **Swiggy**: browse restaurants,
build a cart, checkout with **Razorpay** payments, and track your order live.

| Layer | Tech | Deploy target |
|---|---|---|
| **Backend API** | Django 6.1 · DRF · SimpleJWT · SQLite (dev) / PostgreSQL (prod) | **Render** |
| **Frontend web** | React 19 · Vite 7 · TypeScript | **Firebase Hosting** |
| **Android app** | Same React app wrapped via **Capacitor 7** | Local APK build |
| **Payments** | Razorpay Checkout + server-side signature verification + webhooks | — |

---

## ✨ Features

- 🏪 **Restaurant discovery** — search, Pure-Veg / Open-now filters, sort by rating or delivery time
- 📖 **Menus** with categories, veg/non-veg markers, bestsellers, availability
- 🛒 **Cart** — persists in localStorage, auto-switches when you change restaurants
- 💸 **Razorpay payments** — UPI/cards/netbanking; HMAC signature verification on the server + webhook
  (`payment.captured`) support. Works in **demo mode** with no keys (payments simulated)
- 🧾 **Server-side billing** — item prices/taxes/fees always recomputed on the backend; the client
  cart is never trusted
- 🔐 **Email auth** — JWT access + refresh with auto-refresh and blacklist-on-logout
- 🛵 **Live order tracking** — placed → preparing → out-for-delivery → delivered with polling
- 📱 **Android APK** — the same web app, packaged with Capacitor
- 🌱 **Seed data** — 10 Swiggy-style restaurants with full menus (`python manage.py seed_data`)

### Demo accounts
| Role | Email | Password |
|---|---|---|
| Admin (Django admin) | `admin@foodflow.app` | `admin123` |
| Customer | `demo@foodflow.app` | `demo1234` |

---

## 🚀 Run locally

**Backend** (http://127.0.0.1:8000)
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate            # Windows (use source .venv/bin/activate on macOS/Linux)
pip install -r requirements.txt
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

**Payments in demo mode:** with no `RAZORPAY_KEY_ID`/`RAZORPAY_KEY_SECRET` set, checkout
simulates payment success so the whole flow is testable. To take **real** payments, set the
keys (test keys work for testing with Razorpay test cards/UPI).

---

## ☁️ Deploy to Render (backend)

1. Push this repo to GitHub (see below).
2. [Render dashboard](https://dashboard.render.com) → **New → Blueprint** → pick the repo.
   `render.yaml` at the repo root defines everything: a free PostgreSQL DB (`foodflow-db`) and
   the Django web service (`foodflow-api`). The build runs `collectstatic`, migrations and seed.
3. Fill in the prompted env vars:
   - `CORS_ALLOWED_ORIGINS` → your Firebase URL, e.g. `https://<project>.web.app`
   - `RAZORPAY_KEY_ID` / `RAZORPAY_KEY_SECRET` → from [Razorpay dashboard](https://dashboard.razorpay.com/app/keys)
   - `RAZORPAY_WEBHOOK_SECRET` → Settings → Webhooks (point it at `https://<your-render-app>.onrender.com/api/v1/payments/webhook/`, event: `payment.captured`)
4. Your API will be live at `https://foodflow-api.onrender.com` (health: `/api/v1/health/`).

---

## 🔥 Deploy to Firebase Hosting (frontend web)

1. `npm install -g firebase-tools && firebase login`
2. `firebase use --add` inside `frontend/` → select your project, alias `default`
3. Create `frontend/.env.production`:
   ```
   VITE_API_BASE_URL=https://foodflow-api.onrender.com
   ```
4. Build + deploy:
   ```bash
   cd frontend
   npm run build
   firebase deploy
   ```
5. Add your Firebase URL (e.g. `https://<project>.web.app`) to the backend's
   `CORS_ALLOWED_ORIGINS` on Render.

---

## 🤖 Build the Android APK

The same React app is packaged natively with Capacitor (project in `frontend/android`).

1. Point the app at your live API — `frontend/.env.production`:
   ```
   VITE_API_BASE_URL=https://foodflow-api.onrender.com
   ```
2. Rebuild the web bundle and sync it into the Android project:
   ```bash
   cd frontend
   npm run android:sync        # = npm run build && npx cap sync android
   ```
3. Build the APK:
   - **Android Studio:** `npm run android:open` → *Build → Build App Bundle(s)/APK(s) → Build APK(s)*
   - **CLI** (with JDK 17–21 + Android SDK installed):
     ```bash
     cd android
     gradlew assembleDebug                 # debug APK
     gradlew assembleRelease               # needs signing config (see below)
     ```
   The debug APK lands in `android/app/build/outputs/apk/debug/app-debug.apk`.

4. **Release signing** — create a keystore once, then reference it in
   `android/app/build.gradle` (`signingConfigs.release`) to build installable release APKs:
   ```
   keytool -genkey -v -keystore foodflow.keystore -alias foodflow -keyalg RSA -keysize 2048 -validity 10000
   ```

> Requirements: JDK 17–21 (Android Studio's bundled JBR works), Android SDK 35+.
> `android/local.properties` should contain `sdk.dir=C:\\path\\to\\Android\\Sdk` (it is
> git-ignored; Android Studio creates it automatically).

---

## 🗂 Repo layout

```
├── render.yaml                  # Render blueprint (API + Postgres)
├── backend/
│   ├── config/                  # Django settings/urls/wsgi
│   ├── core/                    # health + API index
│   ├── accounts/                # email auth (register/login/JWT/me)
│   ├── restaurants/             # restaurants, menus, seed_data command
│   └── orders/                  # orders, Razorpay integration, webhook
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
| `/orders/checkout/` | POST | Create order + Razorpay order |
| `/orders/verify-payment/` | POST | Verify Razorpay signature |
| `/orders/` | GET | My orders |
| `/orders/{id}/` | GET | Order detail |
| `/orders/{id}/advance/` | POST | Demo: progress status |
| `/orders/{id}/cancel/` | POST | Cancel order |
| `/payments/webhook/` | POST | Razorpay webhook |
