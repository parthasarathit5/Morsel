# 🍜 Foodiebay

**A Swiggy-style food delivery app — Django REST API + React web + Android APK, with direct UPI payments.**

Browse restaurants, build a cart, pay straight to a merchant UPI ID (no payment gateway account
needed), and track the order from `placed` → `delivered`.

[![Web](https://img.shields.io/badge/live%20web-foodiebay--app--2026.web.app-orange)](https://foodiebay-app-2026.web.app)
[![API](https://img.shields.io/badge/API-Django%206.1%20·%20DRF%20·%20JWT-0c4b33)](backend/)
[![APK](https://img.shields.io/badge/APK-Foodiebay.apk-3ddc84)](./Foodiebay.apk)
[![CI](https://github.com/parthasarathit5/Morsel/actions/workflows/ci.yml/badge.svg)](https://github.com/parthasarathit5/Morsel/actions/workflows/ci.yml)

---

## 🔗 Live links

| What | Where |
|---|---|
| 🌐 **Web app** | **https://foodiebay-app-2026.web.app** |
| 📱 **Android APK** | [`Foodiebay.apk`](./Foodiebay.apk) — 4.2 MB, Android 7.0+ |
| 🔌 **API base** | `https://haven-okay-specialties-wife.trycloudflare.com/api/v1/` |
| ❤️ **API health** | [/api/v1/health/](https://haven-okay-specialties-wife.trycloudflare.com/api/v1/health/) |
| 🖥️ Django admin | [/admin/](https://haven-okay-specialties-wife.trycloudflare.com/admin/) |
| 🔥 Firebase console | [foodiebay-app-2026](https://console.firebase.google.com/project/foodiebay-app-2026/overview) |

> ### ⚠️ Read this first
> The **web app is permanently hosted on Firebase**, but the **Django API is not hosted anywhere
> yet**. It is currently exposed through a free Cloudflare *quick tunnel* to `localhost:8000`
> started on the developer's machine.
>
> * The tunnel URL changes every time it restarts.
> * If the tunnel is down, the web app and APK will load but every API call fails.
>
> To bring it back online (from the repo root):
> ```powershell
> powershell -ExecutionPolicy Bypass -File scripts\share.ps1 -BuildApk
> ```
> This starts the API + tunnel, rewrites `backend/.env` and `frontend/.env.production`, redeploys
> Firebase Hosting and rebuilds the APK with the new URL.
>
> **Fix it for real:** deploy `backend/` to Render (see [Deploy the API](#-deploy-the-api-render)) —
> then the URL is stable and the APK never needs rebuilding.

---

## 🧱 Stack

| Layer | Technology | Deployed to |
|---|---|---|
| **API** | Django 6.1 · Django REST Framework 3.18 · SimpleJWT · `psycopg` 3 | Render (blueprint ready) |
| **Database** | PostgreSQL (Supabase, `sslmode=require`) | Supabase |
| **Web** | React 19 · TypeScript 5.9 · Vite 7 · React Router 7 | Firebase Hosting ✅ |
| **Android** | Capacitor 8 (same React bundle in a native WebView) | Debug APK ✅ |
| **Payments** | Direct UPI (QR + `upi://pay` intent) · Razorpay (optional, auto-enabled by keys) | — |
| **CI** | GitHub Actions (backend checks + seed, frontend build) | GitHub |

---

## 🏗 How it fits together

```text
                    ┌──────────────────────────────┐
                    │  React 19 + Vite (TS)        │
                    │  • /            discovery    │
                    │  • /restaurant/:id           │
                    │  • /cart → /checkout         │
                    │  • /orders, /order/:id       │
                    └───────────┬──────────────────┘
        Firebase Hosting        │  fetch(VITE_API_BASE_URL + /api/v1/…)
        https://…web.app        │  Authorization: Bearer <JWT>
                                ▼
                    ┌──────────────────────────────┐
                    │  Django REST API             │
                    │  accounts · restaurants ·    │
                    │  orders · core               │
                    │  • JWT access/refresh        │
                    │  • server-side bill totals   │
                    │  • UPI intent + Razorpay     │
                    └───────────┬──────────────────┘
                                │  psycopg3 / sslmode=require
                                ▼
                    ┌──────────────────────────────┐
                    │  Supabase PostgreSQL         │
                    └──────────────────────────────┘

   Android:  Capacitor packages the built `dist/` into a WebView (app.foodiebay.mobile)
   Payments: UPI QR / intent pays the merchant VPA directly — no gateway, no fees
```

**Why the bill is trustworthy:** the client only sends `item_id` + `quantity`. Prices, taxes,
delivery fee and the final payable amount are recomputed on the server at checkout — editing
`localStorage` cannot change what you pay.

---

## ✨ Features

**Discovery & menu**
- 🔎 Search, **Pure-Veg**, **Open now** filters, sort by rating or delivery time
- 📖 Category-grouped menus with veg/non-veg markers, bestsellers and availability
- 🏷️ Offers, price-for-two, rating counts, ETA

**Cart & checkout**
- 🛒 Cart persisted in `localStorage`, auto-resets when you switch restaurants
- 🧾 Live bill: item total, delivery fee, GST 5% + platform fee, to-pay
- 🛡️ Delivery-details validation (name / 10-digit phone / address)

**Payments**
- 💸 **UPI (default)** — checkout returns a `upi://pay?pa=…&pn=…&am=…&cu=INR&tn=…` intent plus a
  QR code. Works with GPay / PhonePe / Paytm / any UPI app, money goes **directly to the merchant
  VPA**. Zero gateway fees, no KYC.
- 🧾 **Razorpay (optional)** — set `RAZORPAY_KEY_ID` / `RAZORPAY_KEY_SECRET` and the app switches
  to the official Razorpay Checkout (cards, netbanking, UPI) with **HMAC-SHA256 signature
  verification** server-side and a `payment.captured` webhook endpoint.

**Accounts & orders**
- 🔐 Email-based auth (custom user model), JWT access + refresh with automatic retry on 401,
  case-insensitive login
- 🛵 Order timeline with polling: `placed → preparing → out_for_delivery → delivered`, plus cancel
- 🌱 `seed_data` command: 10 Swiggy-style restaurants with full menus and demo users

---

## 🚀 Quick start (local)

**Prerequisites:** Python 3.13+, Node 20+, npm. Optional for the APK: JDK 17–21 + Android SDK 35+.

### 1. Backend → http://127.0.0.1:8000

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env          # Windows: copy .env.example .env
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

Want SQLite instead of Supabase? Just remove `DATABASE_URL` from `.env` — settings fall back to
`db.sqlite3` automatically.

### 2. Frontend → http://127.0.0.1:5173

```bash
cd frontend
npm install
npm run dev
```

Vite proxies `/api` → `http://127.0.0.1:8000`, so no CORS or env setup is needed in development.

### 3. Log in

| Role | Email | Password |
|---|---|---|
| Customer | `demo@foodiebay.app` | `demo1234` |
| Admin (`/admin/`) | `admin@foodiebay.app` | `admin123` |

> The seed command is idempotent — run it as often as you like.

---

## ⚙️ Configuration

### `backend/.env`

| Variable | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | — (SQLite) | Postgres DSN; URL-encode `@` in the password as `%40` |
| `DJANGO_SECRET_KEY` | dev key | **Change in production** |
| `DJANGO_DEBUG` | `1` locally, `0` on Render | Debug mode / tracebacks |
| `DJANGO_ALLOWED_HOSTS` | — | Extra hosts, comma-separated (`app.onrender.com`, `.trycloudflare.com`) |
| `CORS_ALLOWED_ORIGINS` | `:5173` | Extra browser origins (Firebase, `https://localhost`) |
| `RAZORPAY_KEY_ID` / `_SECRET` | empty | Leave empty for UPI-only mode |
| `RAZORPAY_WEBHOOK_SECRET` | empty | Verifies the `payment.captured` webhook |
| `UPI_VPA` | `7780383832@upi` | Merchant UPI ID that receives the money |
| `UPI_PAYEE_NAME` | `Foodiebay` | Name shown in the UPI app |

### `frontend/.env.production`

| Variable | Purpose |
|---|---|
| `VITE_API_BASE_URL` | Absolute API URL compiled into the bundle. Empty in dev (Vite proxy). |

> This file is committed on purpose: it is public build config, not a secret.

---

## 🔌 API reference (`/api/v1`)

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| `/health/` | GET | — | Liveness probe → `{"status":"ok"}` |
| `/restaurants/` | GET | — | List + `?search=&cuisine=&veg=1&open=1&sort=rating\|delivery_time` |
| `/restaurants/cuisines/` | GET | — | Distinct cuisine list |
| `/restaurants/{id}/` | GET | — | Restaurant + menu categories |
| `/auth/register/` | POST | — | `{email,name,phone,password}` → user + tokens |
| `/auth/token/` | POST | — | `{email,password}` → `{access,refresh}` (case-insensitive) |
| `/auth/token/refresh/` | POST | — | `{refresh}` → new access token |
| `/auth/me/` | GET | ✅ | Current user |
| `/auth/logout/` | POST | ✅ | Blacklists the refresh token |
| `/orders/checkout/` | POST | ✅ | Recomputes bill, creates order, returns UPI intent / Razorpay order |
| `/orders/verify-payment/` | POST | ✅ | Confirms payment (Razorpay signature or UPI confirmation) |
| `/orders/` | GET | ✅ | My orders (paginated) |
| `/orders/{id}/` | GET | ✅ | Order detail + timeline |
| `/orders/{id}/advance/` | POST | ✅ | Demo helper: move to next status |
| `/orders/{id}/cancel/` | POST | ✅ | Cancel an order |
| `/payments/webhook/` | POST | signature | Razorpay `payment.captured` webhook |

### Example: place an order end-to-end

```bash
API=http://127.0.0.1:8000/api/v1

# 1) login
TOKEN=$(curl -s -X POST $API/auth/token/ \
  -H 'Content-Type: application/json' \
  -d '{"email":"demo@foodiebay.app","password":"demo1234"}' | jq -r .access)

# 2) pick a restaurant + item
curl -s $API/restaurants/1/ | jq '.name, .categories[0].items[0] | {name, price, id}'

# 3) checkout (server recomputes totals)
curl -s -X POST $API/orders/checkout/ \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"restaurant_id":1,"items":[{"item_id":1,"quantity":2}],
       "delivery":{"name":"Demo","phone":"9876543210","address":"12 MG Road, Bengaluru"}}' | jq

# → { "order_id": 2, "amount": "612.90", "demo_mode": true,
#     "upi": { "vpa": "7780383832@upi", "intent_url": "upi://pay?pa=…" } }

# 4) confirm the UPI payment
curl -s -X POST $API/orders/verify-payment/ \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"order_id":2}' | jq '.id, .status'
```

---

## 🧪 Tests & CI

```bash
cd backend
pytest                     # 5 API tests: auth, server-side billing, payment verification, privacy
python manage.py check     # Django system checks
```

`.github/workflows/ci.yml` runs on every push/PR: backend `check` → `migrate` → `seed_data`, and
frontend `npm ci` → `tsc -b && vite build`.

---

## ☁️ Deploy the API (Render)

The repo ships `render.yaml`, so Render can create everything as a Blueprint.

1. [Render dashboard](https://dashboard.render.com) → **New → Blueprint** → select this repo.
2. It provisions **`foodiebay-api`** (`rootDir: backend`, gunicorn, health check `/api/v1/health/`).
3. Fill the prompted env vars:

   | Key | Value |
   |---|---|
   | `DATABASE_URL` | Supabase DSN, `@` in the password encoded as `%40` |
   | `CORS_ALLOWED_ORIGINS` | `https://foodiebay-app-2026.web.app,https://foodiebay-app-2026.firebaseapp.com,https://localhost` |
   | `DJANGO_ALLOWED_HOSTS` | `foodiebay-api.onrender.com` |
   | `RAZORPAY_KEY_ID` / `_SECRET` / `_WEBHOOK_SECRET` | optional |
   | `UPI_VPA` / `UPI_PAYEE_NAME` | `7780383832@upi` / `Foodiebay` |

4. After the first deploy, point the frontend at it and rebuild:
   ```bash
   # frontend/.env.production
   VITE_API_BASE_URL=https://foodiebay-api.onrender.com
   ```
   ```bash
   cd frontend && npm run build && firebase deploy --only hosting
   ```
5. Optional Razorpay webhook: **Settings → Webhooks** →
   `https://foodiebay-api.onrender.com/api/v1/payments/webhook/` (event `payment.captured`).

> Free Render instances sleep after ~15 min of inactivity — the first request then takes ~30 s.
> That is fine for a demo; upgrade the plan for always-on.

---

## 🔥 Deploy the web app (Firebase Hosting)

Already live on project **`foodiebay-app-2026`**.

```bash
npm install -g firebase-tools
firebase login
cd frontend
npm run build
firebase deploy --only hosting --project foodiebay-app-2026
```

* `frontend/.firebaserc` pins the project, `firebase.json` sets the `dist` public dir, SPA rewrites
  and cache headers (`/assets/**` immutable, `index.html` no-cache).
* Routing uses `HashRouter`, so deep links work identically on Firebase, Render and inside the APK.

---

## 📱 Android APK

The React app is packaged with Capacitor — `appId: app.foodiebay.mobile`, label **Foodiebay**,
minSdk 24 (Android 7.0), targetSdk 36.

### Build

```bash
cd frontend
npm run build                 # 1. production bundle (uses .env.production)
npx cap sync android          # 2. copy dist + plugins into android/
```

```powershell
cd frontend\android
$env:JAVA_HOME = "C:\Program Files\Android\Android Studio\jbr"   # JDK 17–21; JDK 25 will fail
.\gradlew.bat assembleDebug
```

```text
frontend/android/app/build/outputs/apk/debug/app-debug.apk
```

Or open Android Studio: `npm run android:open` → *Build → Build APK(s)*.

### Install / run

| Device | Steps |
|---|---|
| **Phone (easiest)** | Copy `Foodiebay.apk` to the phone (USB, Drive, WhatsApp to yourself) → tap it → allow **Install unknown apps** for the app you opened it from. |
| **Phone over USB** | `adb devices` then `adb install -r Foodiebay.apk` — needs USB debugging. |
| **Emulator** | Start an AVD, then drag the APK onto the window, or `adb install -r Foodiebay.apk`. |

The launcher icon is **Foodiebay**. Once installed, open it — the bundled web app talks to the API
URL that was compiled in, so rebuild the APK whenever `VITE_API_BASE_URL` changes.

**Release build / Play Store:** create a keystore once, add a `signingConfigs.release` block in
`android/app/build.gradle`, then `gradlew assembleRelease` or `gradlew bundleRelease` (AAB).

```bash
keytool -genkey -v -keystore foodiebay.keystore -alias foodiebay -keyalg RSA -keysize 2048 -validity 10000
```

> **UPI in the APK:** the “Open UPI App 💸” button uses an `upi://pay` intent, which Android hands
> to GPay / PhonePe / Paytm. No extra manifest permission is required.

---

## 🗂 Project structure

```text
.
├── Foodiebay.apk                 # prebuilt debug APK (Android 7+)
├── render.yaml                   # Render Blueprint for the API
├── scripts/
│   └── share.ps1                 # dev tunnel: API + tunnel + Firebase redeploy (+ -BuildApk)
├── .github/workflows/ci.yml      # backend checks + frontend build
├── backend/
│   ├── config/                   # settings (env-driven), urls, wsgi/asgi
│   ├── core/                     # /health/ + API index
│   ├── accounts/                 # custom email user, case-insensitive backend, JWT views
│   ├── restaurants/              # models, serializers, filters, seed_data command
│   ├── orders/                   # order + payment models, billing, UPI/Razorpay, webhook
│   ├── requirements.txt
│   └── pytest.ini
└── frontend/
    ├── src/
    │   ├── api/client.ts         # typed fetch wrapper, JWT + refresh-on-401
    │   ├── context/              # AuthContext, CartContext
    │   ├── pages/                # Home, Restaurant, Checkout, Orders, OrderDetail, Login…
    │   ├── components/           # Navbar, RestaurantCard, MenuItemRow, Badges, Price
    │   └── styles/global.css
    ├── android/                  # Capacitor Android project
    ├── firebase.json / .firebaserc
    └── capacitor.config.ts
```

---

## 🩺 Troubleshooting

| Symptom | Cause / fix |
|---|---|
| Web app loads, data fails | API tunnel is down → run `scripts\share.ps1` (URL changes!) and redeploy. |
| `DisallowedHost` / 400 on API | Add the host to `DJANGO_ALLOWED_HOSTS` (e.g. `.trycloudflare.com`). |
| Browser CORS error | Add the exact origin to `CORS_ALLOWED_ORIGINS` — `https://localhost` is needed for the APK's WebView. |
| `ModuleNotFoundError: psycopg2` | This project uses **psycopg 3** (`psycopg[binary]`); install `requirements.txt`, don't hand-install `psycopg2`. |
| Gradle fails on JDK 25 | Use JDK 17–21, e.g. `$env:JAVA_HOME = "C:\Program Files\Android\Android Studio\jbr"`. |
| APK installs but does nothing | Package id must be `app.foodiebay.mobile` and `MainActivity.java` must live in `java/app/foodiebay/mobile/` — both are fixed in this repo. |
| `illegal character: '\ufeff'` | A Java file was saved with a UTF-8 BOM — re-save without BOM. |
| Supabase connection refused | Free Supabase projects pause when idle; resume from the dashboard. |

---

## 🗺 Roadmap / known limitations

Being explicit about what is *not* done yet:

- [ ] **Host the API permanently** (Render blueprint is ready) so the web app + APK have a stable URL.
- [ ] **Verify UPI payments automatically** — today “I've paid” is a user-confirmed action; a
      real deployment should reconcile against the bank/PSP statement or use Razorpay.
- [ ] **Release-signed APK / Play Store listing** (keystore + `signingConfigs.release`).
- [ ] Restaurant search debouncing, image assets instead of emoji placeholders.
- [ ] Delivery-partner app + push notifications (FCM) for status changes.
- [ ] Admin analytics (orders per day, revenue) beyond the Django admin.

---

## 📄 Notes

Educational demo project. Restaurant/menu data is fictional and seeded; the UPI VPA in the
defaults is a placeholder — replace `UPI_VPA` with your own before accepting real money.
