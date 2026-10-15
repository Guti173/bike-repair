# Repository Instructions

## Project goal

Implement the bicycle repair management prototype defined in `SPEC.md`.

`SPEC.md` is the source of truth for product scope and acceptance criteria.

Do not modify `SPEC.md` unless explicitly requested by the human developer.

## General engineering rules

- Prefer simple and explicit solutions.
- Do not add features that are outside the specification.
- Avoid unnecessary abstractions.
- Keep dependencies minimal.
- Use clear names and small focused functions.
- Code must be written in English.
- The user-facing interface must be written in Spanish.

## Backend

Use:

- Python
- FastAPI
- SQLite
- Pydantic
- pytest

Rules:

- Validate all external input on the server.
- Generate repair order identifiers on the server.
- Represent repair status as a closed enum.
- Reject unexpected input fields.
- Use parameterized database operations or a safe database abstraction.
- Keep persistence logic separate from HTTP routing when practical.
- Return appropriate HTTP status codes.

## Frontend

Use:

- React
- TypeScript
- Vite

Rules:

- Keep the interface simple and functional.
- Avoid unnecessary UI libraries.
- Do not duplicate backend business rules as the only validation mechanism.
- Handle API errors visibly.
- Avoid excessive text, decorative cards, gradients, shadows or unnecessary
  visual complexity.

## Privacy and security

This repository must use synthetic data only.

Never introduce:

- real names;
- real phone numbers;
- real email addresses;
- addresses;
- credentials;
- API keys;
- access tokens;
- secrets.

Do not add personal-data fields to repair orders.

Do not log complete request bodies or repair descriptions unnecessarily.

Do not commit `.env` files, databases containing runtime data or credentials.

Follow least-privilege principles when suggesting permissions or access.

## AI-assisted development

AI-generated changes are proposals, not trusted output.

For each implementation task:

1. Read `SPEC.md` and this file first.
2. State the intended changes before implementing.
3. Stay within the requested task.
4. Run relevant tests after implementation.
5. Report what was changed and what was verified.

Do not weaken or remove tests merely to make an implementation pass.

Do not silently change requirements to accommodate an implementation.

## Testing

Prioritize tests for:

- repair order creation;
- input validation;
- repair order listing;
- valid status changes;
- invalid status changes;
- nonexistent repair orders.

Tests should verify observable behaviour rather than implementation details.

## Scope control

Do not introduce:

- authentication;
- cloud services;
- Docker;
- state-management frameworks;
- component libraries;
- AI features;
- microservices;
- queues;
- caching;
- infrastructure as code;

unless explicitly requested by the human developer.