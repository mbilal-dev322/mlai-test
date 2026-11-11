# Auth API — Django REST Framework + JWT

## Goal and users
A complete authentication REST API: custom email-based user model, JWT login with refresh/logout, email verification, change password and password reset. "Working" = every endpoint verified end-to-end through HTTP against a running server.

## Scope
- In scope: register, login (JWT access+refresh), refresh, logout (blacklist), /me, email verification + resend, change password, reset password (emailed link), superuser seed.
- Out of scope for now: social/OAuth login, rate limiting, tests beyond manual end-to-end verification, email delivery via SMTP (console backend prints emails to the run log), frontend.

## Architecture
- Django 6 + DRF 3.18, `djangorestframework-simplejwt` with token blacklist app (logout/rotation).
- SQLite (`db.sqlite3`) per user choice; swap to Postgres later by changing `DATABASES`.
- Custom user in `accounts/models.py` (`AUTH_USER_MODEL = accounts.User`, email login, `is_verified` flag, `EmailVerificationToken` model).
- All routes under `api/auth/*` (`accounts/urls.py`), console email backend, emails built in `accounts/emails.py` with links pointing to `FRONTEND_URL`.
- Secrets: dev `SECRET_KEY` in settings; for production read from env.

## Routes
- POST /api/auth/register/ → creates user, sends verification email
- POST /api/auth/verify-email/ {token}; POST /api/auth/resend-verification/ {email}
- POST /api/auth/login/ {email,password} → {access, refresh} (403 if unverified)
- POST /api/auth/refresh/ {refresh}; POST /api/auth/logout/ {refresh} (auth)
- GET/PATCH /api/auth/me/ (auth)
- POST /api/auth/change-password/ (auth); POST /api/auth/reset-password/; POST /api/auth/reset-password/confirm/

## Risks and assumptions
- Email verification is enforced at login (403 until verified) — assume that is desired.
- Console email backend: verification/reset links appear in the server log, not a real inbox.

## Phase 1: Full auth flow (this build)
- [x] Scaffold project, custom user model, SQLite migrations
- [x] Register, login, refresh, logout, /me endpoints
- [x] Email verification + resend endpoint
- [x] Change password + password reset flow
- [x] Superuser seeded
- [x] End-to-end verification of all flows via API

Acceptance: register → verify (token from console email) → login → /me → change password → reset password, all through HTTP on the running server.
