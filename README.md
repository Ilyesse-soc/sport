# Sport Coach AI

Application web mobile-first de suivi sportif, nutritionnel et transformation physique avec coach IA.

## Stack

- Frontend: Next.js 16, React 19, TypeScript strict, Tailwind, Recharts, Lucide
- Backend: FastAPI, Pydantic, SQLAlchemy, Alembic
- DB: PostgreSQL
- Auth: JWT backend compatible exchange Supabase (integration prete)
- IA: abstraction AIProvider avec implementation Gemini (gemini-2.5-flash)
- Deploiement: frontend compatible Vercel, backend Docker/Cloud Run

## Architecture

- frontend/
  - src/app
  - src/components
  - src/features
  - src/hooks
  - src/services
  - src/types
  - src/lib
- backend/
  - app/api
  - app/models
  - app/schemas
  - app/services
  - app/repositories
  - app/ai
  - app/core
  - app/database
  - app/utils
  - alembic/

## Fonctionnalites MVP implementees

- Profil utilisateur editable (donnees physiques, objectifs, preferences)
- Dashboard jour: macros, calories, pas, poids, score recup, synthese IA
- Nutrition:
  - ajout repas
  - support poids cru (RAW)
  - base alimentaire de depart
  - recherche aliments
  - analyse assiette photo via Gemini Vision avec incertitude
- Training:
  - bibliotheque exercices
  - log seances, exos, series, reps, charges, RPE/RIR
  - volume par groupe musculaire
  - recommandation progressive overload
- Progression:
  - historique poids et mensurations
  - graphiques poids/taille
  - photos progression (URL stockage)
- Recuperation:
  - sommeil, fatigue, stress, douleurs, motivation
  - score recup
  - pas quotidiens
- Coach IA:
  - chat COACH IA
  - generation bilan journalier
  - generation bilan hebdomadaire
  - logique tool-like backend (fonctions get_today_nutrition, get_nutrition_history, etc.)
- PWA:
  - manifest
  - service worker offline shell
  - installable

## Variables d environnement

Copier [.env.example](.env.example) vers .env a la racine.

Variables principales:

- DATABASE_URL
- JWT_SECRET
- GEMINI_API_KEY
- NEXT_PUBLIC_API_BASE_URL
- NEXT_PUBLIC_SUPABASE_URL
- NEXT_PUBLIC_SUPABASE_ANON_KEY

## Lancement local sans Docker

### Backend

1. Aller dans backend
2. Creer/enclencher venv
3. Installer deps
4. Lancer API

Exemple PowerShell:

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Seed demo:

```powershell
cd backend
.\.venv\Scripts\python.exe app\utils\seed.py
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Application: http://localhost:3000

## Lancement avec Docker Compose

```powershell
docker compose up --build
```

Services:

- frontend: http://localhost:3000
- backend: http://localhost:8000/docs
- postgres: localhost:5432

## Tests et qualite

### Backend

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest -q
```

### Frontend

```powershell
cd frontend
npm run lint
npm run typecheck
npm run test
npm run build
```

## Authentification

- Endpoint backend login/register JWT disponible.
- Frontend propose page auth locale: /auth
- Integration Supabase prete via [frontend/src/lib/supabase.ts](frontend/src/lib/supabase.ts)

## Notes IA et securite

- Cle Gemini jamais exposee au frontend.
- Upload image valide (MIME + taille max).
- Ownership check sur ressources utilisateur via filtre user_id.
- L IA ne diagnostique pas de blessure et renvoie des estimations prudentes pour les photos alimentaires.

## Endpoints principaux

- /api/v1/auth/register
- /api/v1/auth/login
- /api/v1/profile
- /api/v1/profile/goals
- /api/v1/nutrition/foods
- /api/v1/nutrition/meals
- /api/v1/nutrition/daily-summary
- /api/v1/training/workouts
- /api/v1/training/volume
- /api/v1/progression/measurements
- /api/v1/recovery/journal
- /api/v1/recovery/steps
- /api/v1/coach/chat
- /api/v1/coach/analyze-plate
- /api/v1/coach/daily-report
- /api/v1/coach/weekly-report
