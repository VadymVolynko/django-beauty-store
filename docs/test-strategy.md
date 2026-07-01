# Test Strategy

## Current State

`manage.py test` reports `0` tests. The project has test modules, but they are empty.

## Highest Priority Tests

1. Accounts
   - Registration creates inactive user and verification token.
   - Duplicate email is rejected.
   - Expired verification token deletes inactive user.
   - Verified user can log in by email.

2. Cart and Checkout
   - Add, update, remove, clear cart.
   - Invalid or negative quantities are handled safely.
   - Checkout creates order and order items.
   - Cart clears only after successful order creation.
   - Money totals use exact decimal behavior.

3. Booking
   - Appointment requires login.
   - User can only edit/delete own appointments.
   - Appointment date cannot be in the past.
   - Specialist must provide selected service.
   - Duplicate specialist/date/time slots are rejected.

4. Catalog and Reviews
   - Catalog filters by category, brand, and query.
   - Only authenticated users can create reviews.
   - User cannot review same product twice.

5. Wishlist
   - Requires login.
   - Add/remove works idempotently.
   - Redirect targets are constrained to safe local URLs.

## Quality Gates

- Keep `manage.py check` clean.
- Add model/form/view tests before changing checkout, auth, or booking flows.
- Add regression tests for every bug fix in money, auth, appointment ownership, and email verification.

