# NutriGuide (Smart Eats Analyzer) 🥗

NutriGuide is a complete, production-ready full-stack AI-powered nutrition and meal analyzer. Users can snap a food photo or enter a meal description to get instant calorie estimates, macronutrients progress tracking, micro-minerals analysis, personal health scores, and dietary recommendations.

---

## Key Features

1. **AI Visual Food Recognition:** Upload food images (JPG, PNG, WEBP) to automatically detect items, estimate portions, and output nutritional estimates.
2. **Plain-text Analysis:** Type meal descriptions (e.g. *"Grilled chicken breast, rice, broccoli"*) and get structured metrics.
3. **Personalized Dashboard:** Visualize daily calorie logs vs customizable calorie target circles. Track macros (Protein, Carbs, Fats, Fiber) in real-time.
4. **Historical Log:** Search, browse, inspect details of past meal reports, or delete logs.
5. **Macro & Micro mineral evaluate:** Full calculations for Calories, Sugar, Sodium, Iron, Calcium, Magnesium, Potassium, Vitamin A, Vitamin C, Vitamin D, Vitamin B12.
6. **Transparent Scoring:** Rule-based calibration of health scores (0-100) reflecting dietary balance.
7. **Mock AI Provider Mode:** Seamless testing/development even without configured AI keys (mocking matches keywords like "chicken", "pizza", "egg", or defaults to salmon).

---

## Technology Stack

- **Frontend:** React, Vite, TypeScript, Tailwind CSS, React Router, Axios, Recharts, Lucide Icons.
- **Backend:** Python, FastAPI, Pydantic, SQLAlchemy.
- **Database:** PostgreSQL (with SQLite dynamic fallback for quick plug-and-play).
- **AI Integration:** Google Gemini API (`gemini-1.5-flash` for multi-modal text/vision parsing).
- **Infrastructure:** Docker, Docker Compose, Nginx.

---

## Folder Structure

```
nutriguide/
│
├── frontend/             # React Vite Client
│   ├── src/
│   │   ├── components/   # Shared UI parts
│   │   ├── pages/        # Dashboard, Analyzer, Report, History, Profile
│   │   ├── layouts/      # Responsive wrapper
│   │   ├── context/      # AuthContext
│   │   ├── services/     # Axios client configuration
│   │   ├── types/        # TS types
│   │   ├── index.css     # Tailwind styling
│   │   ├── App.tsx       # Routing guards
│   │   └── main.tsx      # DOM mount point
│   ├── Dockerfile
│   ├── nginx.conf
│   └── tsconfig.json
│
├── backend/              # Python FastAPI Server
│   ├── app/
│   │   ├── routes/       # Auth, Analyze, Meals, Dashboard, Profile
│   │   ├── services/     # Gemini, Local Storage, Scoring
│   │   ├── prompts/      # AI Nutrition prompts
│   │   ├── models.py     # SQLAlchemy models
│   │   ├── schemas.py    # Pydantic validation
│   │   └── main.py       # FastAPI application start
│   ├── tests/            # Automated Pytest suite
│   ├── Dockerfile
│   └── requirements.txt
│
├── database/             # Raw DB reference SQL scripts
│   ├── schema.sql
│   └── seed.sql
│
├── docker-compose.yml    # Orchestrated compose
└── README.md             # Setup guide
```

---

## Quick Start Setup (Without Docker)

NutriGuide supports a zero-config setup using SQLite. This allows running tests and local code without PostgreSQL installed.

### 1. Run Backend Server
Ensure Python 3.10+ is installed:
```powershell
cd backend
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Install requirements
pip install -r requirements.txt
# Start server (automatically creates SQLite db and mounts uploads)
uvicorn app.main:app --reload
```
The backend API is now running at `http://localhost:8000`. You can inspect raw documentation Swagger at `http://localhost:8000/docs`.

### 2. Run Frontend Client
Ensure Node.js v18+ is installed:
```powershell
cd frontend
npm install
npm run dev
```
Open your browser at `http://localhost:5173`. Vite proxies API calls automatically to backend.

---

## Running with Docker Compose (PostgreSQL)

Build and boot the entire stack (Postgres Database, FastAPI Server, React + Nginx frontend) in single command:

```bash
docker-compose up --build
```
- **Web App:** Available at `http://localhost:80` (or simply `http://localhost`).
- **Backend Swagger:** Available at `http://localhost:8000/docs`.
- **Database:** Postgres running on port `5432` with username `postgres`, password `postgres`.

---

## Configuring AI Providers

By default, if no `AI_API_KEY` is configured in your `.env` (or environment), the backend executes using **MockAIProvider** so you can click around and analyze meals without paying anything.

To enable the real Gemini AI model:
1. Obtain a Gemini API Key from Google AI Studio.
2. Edit `backend/.env` (or set environment variables):
   ```env
   AI_API_KEY=YOUR_GEMINI_API_KEY_HERE
   AI_PROVIDER=gemini
   ```
3. Restart the backend service. The system will now route analysis queries directly to Gemini.

---

## Running Automated Tests

A complete suite of tests evaluates Auth register/login gates, Log history additions, deletion validations, and Mock calculations:

```powershell
cd backend
# Make sure virtual environment is active
pytest -v
```
