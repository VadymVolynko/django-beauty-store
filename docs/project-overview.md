# Project Overview

## Summary

Beauty Store is a Django monolith for a beauty e-commerce and appointment-booking flow. The project uses Django apps to separate accounts, catalog, cart, orders, booking, reviews, and wishlist features. Rendering is server-side through templates under `templates/`, with static assets under `static/` and uploaded media under `media/`.

## Django Apps

- `accounts`: registration, email verification, email-based login, logout, profile.
- `catalog`: home page, product catalog, product detail page, product review creation.
- `cart`: session-backed shopping cart.
- `orders`: checkout, order creation, confirmation email, order history.
- `booking`: services, specialists, appointment create/list/update/delete.
- `reviews`: review model and review form for products.
- `wishlist`: authenticated wishlist add/remove/list.

## URL Map

- `/`: home page.
- `/catalog/`: catalog with category, brand, and search filters.
- `/catalog/<slug>/`: product detail and authenticated review creation.
- `/accounts/register/`: registration and verification email send.
- `/accounts/login/`: login by email.
- `/accounts/logout/`: logout.
- `/accounts/profile/`: authenticated profile.
- `/accounts/verify/<uuid>/`: email verification.
- `/booking/services/`: services list.
- `/booking/specialists/`: specialists list.
- `/booking/appointments/`: authenticated appointment list.
- `/booking/appointments/book/`: authenticated appointment creation.
- `/booking/appointments/<id>/edit/`: owner-only appointment edit.
- `/booking/appointments/<id>/cancel/`: owner-only appointment delete.
- `/cart/`: session cart.
- `/cart/add/<product_id>/`: add product to cart.
- `/cart/remove/<product_id>/`: remove product from cart.
- `/cart/update/<product_id>/`: update product quantity.
- `/checkout/`: checkout.
- `/orders/success/<id>/`: order success page.
- `/orders/`: authenticated order history.
- `/wishlist/`: authenticated wishlist.
- `/wishlist/add/<product_id>/`: add product to wishlist.
- `/wishlist/remove/<product_id>/`: remove product from wishlist.

## Main Findings

- `config/settings.py` contains a hard-coded Django `SECRET_KEY` and SMTP credentials. Move these into environment variables before sharing or deploying.
- `DEBUG = True` and `ALLOWED_HOSTS = []` are development-only settings.
- `orders.views.checkout_view` creates `OrderItem` rows with `product=None`, even though the cart item contains product id data. This preserves order snapshots but loses product relationship for later analytics/admin navigation.
- `cart.cart.Cart` stores prices as strings but calculates totals through `float`; use `Decimal` to avoid money rounding issues.
- `booking.forms.AppointmentForm` does not validate future dates, service/specialist compatibility, or slot conflicts.
- `wishlist.views` redirects to `HTTP_REFERER` / posted `next` without host validation. Prefer `url_has_allowed_host_and_scheme` or named-route fallbacks.
- Email sending is inconsistent: registration fails loudly, while booking/orders use `fail_silently=True`. That can hide production mail failures.
- Locale strings in several files appear mojibake-encoded, for example Ukrainian language label and some display strings. Check file encoding and translations.

## Verification

- System check passed with no Django issues.
- Test runner found `0` tests, so behavior is currently unprotected by automated tests.

