# Beauty Store

A full-featured beauty e-commerce platform built with Django — includes a cosmetics shop and an online booking system for cosmetology services.

## Live Demo

> _Screenshot of home page_
>
> _(add screenshots after running locally)_

---

## Features

**Shop**
- Product catalog with categories, brands, and filters
- Product detail pages with images
- Session-based shopping cart (add / update / remove)
- Checkout flow with delivery details
- Order history for authenticated users

**Booking**
- Browse available cosmetology services with pricing and duration
- Specialist profiles with photo, bio, and linked services
- Book appointments (date + time + comment)
- View, edit, and cancel pending appointments from personal cabinet

**Accounts**
- Registration and login / logout
- Personal profile page
- Order history and appointment list in one place

**Admin panel**
- Full CRUD for products, categories, brands
- Order management with inline order items and status editing
- Appointment management with date hierarchy and status filter

---

## Tech Stack

- **Backend:** Python 3.12 / Django 6.0
- **Database:** SQLite (dev) — swap `DATABASES` for PostgreSQL in production
- **Frontend:** Bootstrap 5.3, custom CSS (light/dark theme)
- **Storage:** Pillow for image uploads

---

## Installation

```bash
git clone https://github.com/VadymVolynko/beauty-service
cd beauty-service

python -m venv venv
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser   # optional — for admin access
python manage.py runserver
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

---

## Project Structure

```
beauty-store/
├── config/          # Django settings, root URLs, wsgi
├── catalog/         # Product, Category, Brand models + views
├── cart/            # Session-based cart logic
├── orders/          # Order & OrderItem models, checkout views
├── booking/         # Service, Specialist, Appointment models + views
├── accounts/        # Auth views (register / login / profile)
├── templates/       # All HTML templates
├── static/          # CSS, JS, images
├── media/           # Uploaded product/specialist images
└── manage.py
```

---

## DB Structure

```
Category  ──┐
Brand     ──┤── Product
             └──────────────── OrderItem ──── Order ── User
                                                          │
Service ──────────────────────────────────── Appointment─┘
   │                                              │
Specialist ───── Specialist.services (M2M) ───────┘
```

> _Attach draw.io diagram screenshot here_

---

## Pages Screenshots

| Page | Description |
|------|-------------|
| `/` | Home — hero + featured products |
| `/catalog/` | Product catalog grid |
| `/catalog/<slug>/` | Product detail with add-to-cart |
| `/cart/` | Shopping cart with quantity controls |
| `/checkout/` | Checkout form |
| `/orders/history/` | My orders (auth required) |
| `/booking/services/` | Services list with "Book now" |
| `/booking/specialists/` | Specialist profiles |
| `/booking/appointments/book/` | Appointment booking form |
| `/booking/appointments/` | My appointments (auth required) |
| `/accounts/login/` | Login / Register (tabs) |
| `/accounts/profile/` | User profile |

> _Add screenshots for each page in the PR description_

---

## Contributing

PRs are welcome. Please open an issue first to discuss what you would like to change.
