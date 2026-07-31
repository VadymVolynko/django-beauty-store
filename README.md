# Beauty Store

A full-featured beauty e-commerce & booking platform built with Django — a cosmetics shop with reviews and wishlists, an online booking system for cosmetology services, and a separate owner dashboard for store analytics and product management. Access to the storefront is gated behind sign-in (with a one-click demo login in development mode), which makes it easy to share as a portfolio demo without exposing it publicly. The UI is fully localized in English and Ukrainian.

## Live Demo

**[https://beauty-store-4jzw.onrender.com](https://beauty-store-4jzw.onrender.com)** — hosted on Render's free tier, so the first request after a period of inactivity can take up to a minute to spin the instance back up. See [Test account for reviewers](#deployment-render) below to sign in.

![Home page](docs/screenshots/home.png)

---

## Features

**Shop**
- Browse brands, then filter that brand's products by category or search
- Product detail pages with images, ratings, and reviews
- Wishlist — save / remove products (auth required)
- Session-based shopping cart (add / update / remove)
- Checkout flow with delivery details, stock validation, inventory decrement, and double-submit protection
- Order history for authenticated users

**Booking**
- Browse available cosmetology services with pricing and duration
- Specialist profiles with photo, bio, gallery, and linked services
- Book appointments (date + time + comment) with past-date, specialist-service, and double-booking validation
- View, edit, and cancel pending appointments from personal cabinet

**Accounts**
- Registration with email verification (token-based, expires after 24h)
- Login / logout, personal profile page
- Order history and appointment list in one place
- The storefront requires sign-in to browse; in local portfolio preview mode (`DJANGO_DEBUG=True` and `ENABLE_DEMO_LOGIN=True`) any email/password creates and logs in a throwaway demo account for quick evaluation

**Owner Dashboard**
- Separate owner login, independent of regular user accounts
- Store analytics: revenue, order count, appointments (incl. pending), products, items sold, top-selling products
- Recent orders and appointments overview
- Full product CRUD (create / edit / delete), outside of the Django admin

**Localization**
- English / Ukrainian language switch (Django i18n + `LocaleMiddleware`)

**Admin panel**
- Full CRUD for products, categories, brands
- Order management with inline order items and status editing
- Appointment management with date hierarchy and status filter

---

## Tech Stack

- **Backend:** Python 3.12+ / Django 6.0.6
- **Database:** SQLite (dev) — swap `DATABASES` for PostgreSQL in production
- **Frontend:** Bootstrap 5.3, custom CSS (light/dark theme)
- **Images:** Pillow for image uploads
- **Config:** python-decouple (`.env`-based settings)

---

## Installation

```bash
git clone https://github.com/VadymVolynko/django-beauty-store
cd django-beauty-store

python -m venv venv
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
# then edit .env: set DJANGO_SECRET_KEY, and OWNER_LOGIN / OWNER_PASSWORD
# for access to the owner dashboard

python manage.py migrate
python manage.py createsuperuser   # optional — for Django admin access
python manage.py populate_db       # optional — seeds sample catalog & booking data
python manage.py runserver
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser. The storefront requires sign-in — in local portfolio preview mode (`DJANGO_DEBUG=True` and `ENABLE_DEMO_LOGIN=True`) any email/password combination logs you in as a demo user, or sign in with your `OWNER_LOGIN` / `OWNER_PASSWORD` for the owner dashboard.

---

## Deployment (Render)

**Live app:** [https://beauty-store-4jzw.onrender.com](https://beauty-store-4jzw.onrender.com)

The app is deployed on [Render](https://render.com/docs/deploy-django) using the included `render.yaml` blueprint (New → Blueprint, point it at this repo — provisions a free web service and a free Postgres database). To deploy your own copy, either use that blueprint or set it up manually:

- **Build command:** `./build.sh` (installs dependencies, runs `collectstatic`, runs `migrate`, seeds sample catalog/booking data, and creates/resets a standing test user)
- **Start command:** `gunicorn config.wsgi:application`
- **Environment variables:** `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=False`, `ENABLE_DEMO_LOGIN=False`, `DATABASE_URL` (from a Render Postgres instance), plus any of the email/owner-login vars from `.env.example` you want in production. `ALLOWED_HOSTS`/`CSRF_TRUSTED_ORIGINS` don't need to be set manually — the app trusts Render's own `RENDER_EXTERNAL_HOSTNAME` automatically.

**Test account for reviewers** (since `ENABLE_DEMO_LOGIN` is off in production, sign in requires a real, verified account — `build.sh` creates one on every deploy so nobody needs email access to check out the site):
```
login: user@example.com
password: user12345
```

Note: Render's filesystem is ephemeral, so uploaded media (product/specialist images added after deploy) won't persist across deploys/restarts — attach a persistent disk or move `MEDIA` to object storage (e.g. S3) for real production use.

---

## Security Notes

- Order success pages are protected: authenticated users can only view their own orders, while guest checkout success is limited to recent order ids stored in that browser session.
- Owner access uses a separate session flag, ignores empty owner passwords, and temporarily locks the owner login after repeated failed attempts.
- Demo login is controlled by `ENABLE_DEMO_LOGIN` and only runs when `DJANGO_DEBUG=True`; disable it for any shared staging or production deployment.
- Production security settings are configured through environment variables: `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SECURE_SSL_REDIRECT`, and HSTS options.

## Quality

- GitHub Actions CI runs Django system checks and the test suite on pushes to `main`, `master`, `develop`, and on pull requests.
- Checkout tests cover order creation, stock updates, unavailable/out-of-stock products, duplicate submit protection, and order success permissions.
- Booking tests cover appointment creation, user isolation, past-date rejection, specialist/service validation, and double-booking prevention.

---

## Project Structure

```
beauty-store/
├── config/          # Django settings, root URLs, wsgi
├── catalog/         # Product, Category, Brand models + views, owner product management
├── cart/            # Session-based cart logic
├── orders/          # Order & OrderItem models, checkout views
├── booking/         # Service, Specialist, Appointment models + views
├── accounts/        # Auth views (register / login / profile / owner dashboard)
├── reviews/         # Product review & rating model + form
├── wishlist/        # Wishlist model + views
├── templates/       # All HTML templates
├── static/          # CSS, JS, images
├── media/           # Uploaded product/brand/specialist images
├── locale/           # EN/UA translation catalogs
├── docs/            # Data model notes
└── manage.py
```

---

## DB Structure

```mermaid
erDiagram
    USER {
        int id PK
        string username
        string email
        string phone_number
        bool is_staff
    }
    EMAILVERIFICATIONTOKEN {
        int id PK
        uuid token
        datetime created_at
    }
    CATEGORY {
        int id PK
        string name
        string slug
    }
    BRAND {
        int id PK
        string name
        string slug
        string description
    }
    PRODUCT {
        int id PK
        string name
        string slug
        decimal price
        int stock
        bool is_available
        bool is_featured
    }
    ORDER {
        int id PK
        string status
        decimal total_price
        string email
    }
    ORDERITEM {
        int id PK
        string name
        decimal price
        int quantity
    }
    SERVICE {
        int id PK
        string name
        decimal price
        int duration
    }
    SPECIALIST {
        int id PK
        string name
        int experience
    }
    SPECIALISTPHOTO {
        int id PK
        int order
    }
    APPOINTMENT {
        int id PK
        date date
        time time
        string status
    }
    REVIEW {
        int id PK
        int rating
        string text
    }
    WISHLISTITEM {
        int id PK
        datetime added_at
    }

    USER ||--o| EMAILVERIFICATIONTOKEN : has
    USER ||--o{ ORDER : places
    USER ||--o{ APPOINTMENT : books
    USER ||--o{ REVIEW : writes
    USER ||--o{ WISHLISTITEM : saves

    CATEGORY ||--o{ PRODUCT : groups
    BRAND ||--o{ PRODUCT : groups
    PRODUCT ||--o{ ORDERITEM : "sold as"
    PRODUCT ||--o{ REVIEW : "reviewed via"
    PRODUCT ||--o{ WISHLISTITEM : "saved via"

    ORDER ||--o{ ORDERITEM : contains

    SERVICE ||--o{ APPOINTMENT : "booked for"
    SPECIALIST ||--o{ APPOINTMENT : "assigned to"
    SPECIALIST ||--o{ SPECIALISTPHOTO : "gallery"
    SPECIALIST }o--o{ SERVICE : offers
```

---

## Pages Screenshots

| Page | Description | Screenshot |
|------|-------------|------------|
| `/` | Home — hero + featured products (sign-in required) | <img src="docs/screenshots/home.png" width="320"> |
| `/catalog/` | Brand list | <img src="docs/screenshots/catalog-brands.png" width="320"> |
| `/catalog/brand/<slug>/` | Brand's products, filterable by category and search | <img src="docs/screenshots/catalog-brand-products.png" width="320"> |
| `/catalog/<slug>/` | Product detail — add to cart, wishlist, reviews | <img src="docs/screenshots/product-detail.png" width="320"> |
| `/cart/` | Shopping cart with quantity controls | <img src="docs/screenshots/cart.png" width="320"> |
| `/checkout/` | Checkout form | <img src="docs/screenshots/checkout.png" width="320"> |
| `/orders/` | My orders (auth required) | <img src="docs/screenshots/orders.png" width="320"> |
| `/wishlist/` | My wishlist (auth required) | <img src="docs/screenshots/wishlist.png" width="320"> |
| `/booking/services/` | Services list with "Book now" | <img src="docs/screenshots/booking-services.png" width="320"> |
| `/booking/specialists/` | Specialist profiles | <img src="docs/screenshots/booking-specialists.png" width="320"> |
| `/booking/appointments/book/` | Appointment booking form | <img src="docs/screenshots/booking-appointment-form.png" width="320"> |
| `/booking/appointments/` | My appointments (auth required) | <img src="docs/screenshots/booking-my-appointments.png" width="320"> |
| `/accounts/login/`, `/accounts/register/` | Login / Register (tabs) | <img src="docs/screenshots/auth-login.png" width="320"> |
| `/accounts/profile/` | User profile | <img src="docs/screenshots/profile.png" width="320"> |
| `/owner/` | Owner dashboard — analytics, recent orders & appointments (owner login required) | <img src="docs/screenshots/owner-dashboard.png" width="320"> |
| `/owner/products/` | Owner product management — list, add, edit, delete | <img src="docs/screenshots/owner-products.png" width="320"> |

---

## Contributing

PRs are welcome. Please open an issue first to discuss what you would like to change.
