# Production Readiness Audit

Repository: `22f2001379/household-services`

## Executive Summary

The project is a Flask API with a Vue 2/Vite frontend for household service booking and administration. The original codebase was a working prototype, but it had production blockers around credential handling, hardcoded secrets, unauthenticated state-changing endpoints, brittle null handling, tracked runtime artifacts, missing tests, and incomplete developer documentation.

## Critical Findings

- Passwords were stored and compared in plaintext instead of using the configured Flask-Security password hashing.
- `SECRET_KEY`, password salt, SMTP placeholders, Redis URLs, and default admin credentials were hardcoded in source code.
- Service, user, request, and review mutations were callable without authentication or role authorization.
- A predictable seeded admin account (`admin@me.com` / `adminme`) was created automatically.
- A live SQLite database and Python bytecode were committed to the repository.
- API handlers returned raw exception strings, leaking implementation details.

## Bugs and Reliability Issues

- Professional listing could crash when a professional had no requests or reviews.
- Rating lookups used the wrong identifier in professional request serialization.
- Review text was lost because the frontend sent `reviewText` while the backend expected `review_text`.
- Service request creation did not validate service, customer, professional, or date inputs before writing.
- Several update endpoints did not check that target records existed.
- Role naming was inconsistent (`professional` vs `service_professional`).
- Login and registration responses did not match the frontend token expectations.
- Several frontend API methods pointed to endpoints that did not exist.
- `AdminDashboard.vue` contained invalid template syntax.

## Security Issues

- CORS was configured on an initial Flask app instance that was later discarded.
- CSRF was disabled without clear token-auth configuration.
- User-provided role names were accepted during registration.
- User update/delete endpoints allowed privilege changes without authorization.
- Console logs and `print()` calls exposed user data and request payloads.

## Architecture and Maintainability Issues

- `backend/app.py` created two app instances and initialized extensions against the wrong one.
- Route handlers mixed validation, authorization, serialization, persistence, and response shaping.
- `resources.py` duplicated `Api` instances and contained unused prototype endpoints.
- Role state is stored both as a many-to-many relationship and `role_id`, which can drift.
- Old prototype files and unused components increased repository noise.
- Backend/frontend naming conventions were inconsistent.

## Performance Issues

- Endpoints performed N+1 queries for ratings and related request data.
- Frontend tables resolved related customer/professional data through nested render loops.
- SQLite is fine for development, but production database guidance was absent.

## UI/UX and Accessibility Issues

- Dashboard tables have limited responsive behavior.
- Hand-rolled modals lack complete focus management and keyboard handling.
- Most views had limited empty, loading, and error states.
- Dates were rendered as raw JavaScript `Date` objects.
- Search assumed nullable fields were always present.

## Dependency and Tooling Issues

- Vue 2 is end-of-life.
- Vite 2 and Vue 2 build tooling still carry audit findings that require a breaking migration to fully eliminate.
- No backend tests or test runner documentation existed.
- Root setup/build/test/deployment documentation was missing.

## Testing Gaps

- No tests existed for authentication, role enforcement, service management, service requests, or reviews.
- No CI workflow existed to run backend tests and frontend builds.

## Remediation Priorities Applied

1. Replace hardcoded configuration with environment-driven config.
2. Hash passwords and return token-auth login responses.
3. Gate state-changing endpoints by role.
4. Add request validation and safe serializers.
5. Remove tracked runtime/generated files.
6. Add backend tests for critical API flows.
7. Fix frontend API contract mismatches and build-breaking syntax.
8. Rewrite README with complete setup and operating guidance.
