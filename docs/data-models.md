# Data Models

## Catalog

- `Category`: `name`, unique `slug`.
- `Brand`: `name`, unique `slug`, optional description, optional image.
- `Product`: category, brand, name, unique slug, description, price, image, stock, availability, featured flag, timestamps.

## Accounts

- `User`: custom user model (`AUTH_USER_MODEL = "accounts.User"`), extends Django's `AbstractUser` with an extra `phone_number` field.
- `EmailVerificationToken`: one-to-one `User`, UUID token, creation timestamp, 24-hour expiry helper.

## Orders

- `Order`: optional user, customer contact/shipping fields, status, total price, timestamps.
- `OrderItem`: order, optional product, snapshot name, price, quantity, computed total.

## Booking

- `Service`: name, description, price, duration.
- `Specialist`: name, bio, optional photo, experience, many-to-many services.
- `SpecialistPhoto`: specialist, image, display order — gallery photos shown on the specialist's profile.
- `Appointment`: user, specialist, service, date, time, status, comment, creation timestamp.

## Reviews

- `Review`: product, user, rating from 1 to 5, text, creation timestamp.
- Constraint: one review per product/user pair.

## Wishlist

- `WishlistItem`: user, product, added timestamp.
- Constraint: one wishlist entry per product/user pair.

## Relationship Notes

- The catalog is central: products connect to cart, orders, reviews, and wishlist.
- Orders snapshot product name/price, which is good for historical records, but current checkout does not keep the product foreign key.
- Appointments link users to both service and specialist, but the model does not enforce unique appointment slots.

