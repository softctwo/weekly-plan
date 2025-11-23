# Repository Guidelines

## Project Structure & Module Organization
- `backend/`: FastAPI app under `app/` (API routes, core config, models, schemas, services, utils); tests live in `backend/tests`; scripts `run.sh`, `run_tests.sh`, `init_db.py`; env template `.env.example`.
- `frontend/`: Vue 3 + Vite under `src/` (router, store via Pinia, views, shared components); Vitest specs in `tests/`, Playwright flows in `e2e/`; build output `dist/`.
- Root docs (README, PRD, testing reports) capture product scope; `docker-compose.yml` reserved for multi-service runs.

## Build, Test, and Development Commands
**Backend**
- Setup: `cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt`.
- Serve: `cd backend && ./run.sh` (use `./run.sh init` once to seed DB and default admin `admin/admin123`; port 8000).
- Test: `cd backend && ./run_tests.sh coverage` for pytest + coverage (`htmlcov/index.html`), or `./run_tests.sh quick` for faster cycles.

**Frontend**
- Setup: `cd frontend && npm install`.
- Dev: `npm run dev` (Vite on 5173, proxying API to 8000).
- Build/preview: `npm run build` then `npm run preview`.
- Quality: `npm run lint`; unit `npm run test`; E2E `npm run test:e2e` (headed/ui flags available).

## Coding Style & Naming Conventions
- Python: 4-space indent; async FastAPI handlers where possible; snake_case modules and function names; prefer type hints and Pydantic schemas; keep settings in env-driven config under `app/core`.
- Vue: 2-space indent, single quotes; components PascalCase; routes kebab-case; Pinia stores in `store/`; shared API clients under `src/api`.
- Tests: backend `test_*.py` (markers in `pytest.ini`); frontend `*.test.js`/`*.spec.js`. Avoid committing `dist/`, `venv/`, `node_modules/`, or local DBs.

## Testing Guidelines
- Backend markers: `unit`, `api`, `model`, `integration`, `auth`, `slow`; use `ENV_FILE=.env.test`. Cover auth, DB transactions, and role → task rules; watch coverage in `htmlcov/index.html`.
- Frontend: Vitest with happy-dom/jsdom for components (mock HTTP via axios); Playwright in `frontend/e2e` for auth → dashboard → tasks flows. Document new or changed cases in PRs.

## Commit & Pull Request Guidelines
- Git history favors concise lines (`fix: ...`, imperative summaries); follow `type: short action` (`feat`, `fix`, `chore`, `docs`, `test`) in English or Chinese consistently and keep commits focused.
- PRs should state scope, linked issue, setup steps, and commands run; attach screenshots/GIFs for UI changes; call out schema/env changes and expected impact.

## Security & Configuration Tips
- Never commit secrets or `.env`; start from `.env.example` and rotate default admin after seeding.
- SQLite is default; adjust DSN for PostgreSQL/Docker. Exclude `weekly_plan.db` and sensitive logs from commits.
