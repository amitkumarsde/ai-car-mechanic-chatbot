# AI Car Mechanic Chatbot

## Project overview

- A web chatbot where a car owner chats with a virtual senior mechanic.
- The bot asks follow-up questions, gives a diagnosis, suggests a repair and books a mechanic.
- Common problems are answered with normal backend rules. Google Gemini is used **only** when rules cannot help (unknown problems, photos, audio and video).

## Features

- Home page with common car problems that open the chat in one click
- Chat that only answers car questions and politely rejects other topics
- Follow-up questions before a diagnosis, with a "Skip questions and diagnose now" option
- Upload photos, engine sounds (audio) and videos for AI analysis
- Diagnosis with problem, service, cost range and urgency
- "Book Mechanic" button after a diagnosis (one booking per diagnosis)
- Chat history, diagnosis history and booking details page
- Each reply shows "Instant answer" (rules) or "AI answer" (Gemini)
- If the main AI model is busy, a backup model is tried; if both fail, a friendly message is shown

## Tech stack

- **Frontend:** Next.js 16, React 19, TypeScript, Tailwind CSS, Lucide React (icons)
- **Backend:** Python 3.12, Django 6, Django REST Framework
- **Database:** SQLite
- **AI:** Google Gemini (`google-genai`)
- **Hosting:** Vercel (frontend), PythonAnywhere (backend)
- **Tests:** Django test runner (backend), Node test runner (frontend), GitHub Actions CI

## Project structure

```
ai-car-mechanic-chatbot/
├── backend/
│   ├── config/              Django settings, main URLs and WSGI entry point
│   ├── chat/
│   │   ├── models.py        Database tables (Model)
│   │   ├── serializers.py   Input validation and JSON output
│   │   ├── views.py         API endpoints (Controller)
│   │   ├── urls.py          /api/ routes
│   │   ├── exceptions.py    One error format for all APIs
│   │   ├── admin.py         Manage bookings in /admin
│   │   ├── tests.py         Backend tests
│   │   └── services/
│   │       ├── chatbot.py   Chat flow: rules first, AI last
│   │       ├── knowledge.py Car problems, questions and causes
│   │       ├── gemini.py    The only file that calls Gemini
│   │       └── media.py     Upload type, size and content checks
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   └── src/
│       ├── app/             Pages: / (home), /chat, /history, /booking/[id]
│       ├── components/      Header, footer, chat window, input, messages, diagnosis card, booking form, history
│       ├── hooks/useChat.ts Chat state and actions
│       └── lib/             API client, types, file checks, browser id
└── .github/workflows/ci.yml Runs all tests on every push
```

## Setup

- Install **Python 3.12+** and **Node.js 20+**.
- Get a free Gemini API key from <https://aistudio.google.com/apikey> (optional: without it, rule-based chat still works).

**Backend**

```bash
cd backend
python -m venv venv
venv\Scripts\activate            # Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
copy .env.example .env           # Mac/Linux: cp .env.example .env
python manage.py migrate         # creates db.sqlite3
python manage.py createsuperuser # optional, for /admin
```

**Frontend**

```bash
cd frontend
npm install
copy .env.example .env.local     # Mac/Linux: cp .env.example .env.local
```

## Environment variables

**Backend (`backend/.env`)**

- `DEBUG` - `True` on your computer, `False` when deployed
- `DJANGO_SECRET_KEY` - long random secret (required when `DEBUG=False`)
- `ALLOWED_HOSTS` - domains that can reach the API, e.g. `localhost,127.0.0.1`
- `CORS_ALLOWED_ORIGINS` - frontend URL, e.g. `http://localhost:3000`
- `CSRF_TRUSTED_ORIGINS` - API URL with https (only needed for `/admin` when deployed)
- `GEMINI_API_KEY` - your Gemini key
- `GEMINI_MODEL` - main model (default `gemini-3.5-flash-lite`)
- `GEMINI_FALLBACK_MODEL` - backup model when the main one is busy (default `gemini-3.1-flash-lite`)
- `SQLITE_PATH`, `MEDIA_ROOT`, `STATIC_ROOT` - optional; leave empty to keep them inside the `backend` folder
- `NUM_PROXIES` - `1` on PythonAnywhere (it has a proxy in front), empty locally

**Frontend (`frontend/.env.local`)**

- `NEXT_PUBLIC_API_URL` - backend API URL, e.g. `http://127.0.0.1:8000/api`

## Run commands

| Task | Command |
|---|---|
| Start backend | `cd backend` then `python manage.py runserver` |
| Start frontend | `cd frontend` then `npm run dev` |
| Open the app | <http://localhost:3000> |
| Backend tests | `cd backend` then `python manage.py test chat` |
| Frontend tests | `cd frontend` then `npm test` |
| Frontend lint | `cd frontend` then `npm run lint` |
| Frontend build | `cd frontend` then `npm run build` |

- Restart the backend after changing `.env`.
- Tests mock Gemini, so they need no API key or internet.

**Where data is saved**

- Chats, diagnoses and bookings: `backend/db.sqlite3`
- Uploaded files: `backend/media/uploads/`
- Both are in `.gitignore` and never go to GitHub.

## API endpoints

- Every request needs the header `X-Client-Id: <uuid>`. The frontend creates it once per browser, and users only see their own data.
- Errors always look like `{"error": {"message": "...", "details": {...}}}`.

| Method | URL | What it does |
|---|---|---|
| GET | `/api/health/` | Health check |
| POST | `/api/chat/` | Send a message (`message`, optional `conversation_id`, optional `media_ids`) and get the bot reply |
| POST | `/api/upload/` | Upload one file (`file`) as multipart form data; returns its `id` for `media_ids` |
| POST | `/api/diagnosis/` | Get a diagnosis now for a `conversation_id` |
| GET | `/api/diagnosis/` | Diagnosis history |
| POST | `/api/booking/` | Book a mechanic (name, phone, car model, address, date, time slot) |
| GET | `/api/booking/{id}/` | Booking details |
| GET | `/api/conversations/` | Chat history list |
| GET | `/api/conversations/{id}/` | One chat with all messages |

**Upload limits**

- Images: jpg, jpeg, png, webp (max 5 MB)
- Audio: mp3, wav, m4a, ogg, webm (max 10 MB)
- Video: mp4, mov, webm (max 15 MB)
- Up to 3 files per message, 15 MB in total. File content is checked, not just the name.

**Rate limits (per IP):** chat 20/min, upload 10/min, others 60/min.

## Basic deployment

**Why PythonAnywhere and not AWS**

- AWS signup needs a credit or debit card for verification, which was not available for this project.
- PythonAnywhere's free plan needs no card.
- It keeps files on a permanent disk, so the SQLite database and uploaded media are not lost on restart.
- It allows calls to the Gemini API (`*.googleapis.com`) from free accounts.
- It gives free HTTPS and a ready web address (`YOURNAME.pythonanywhere.com`), so no server or domain setup is needed.

**Backend on PythonAnywhere**

- Create a free **Beginner** account at <https://www.pythonanywhere.com>.
- Open a **Bash console** and run:
  - `git clone https://github.com/YOUR_GITHUB/ai-car-mechanic-chatbot.git`
  - `cd ai-car-mechanic-chatbot/backend`
  - `python3.12 -m venv venv && source venv/bin/activate`
  - `pip install --no-cache-dir -r requirements.txt`
- Create `backend/.env` with:
  - `DEBUG=False` and a new `DJANGO_SECRET_KEY`
  - `ALLOWED_HOSTS=YOURNAME.pythonanywhere.com`
  - `CORS_ALLOWED_ORIGINS=https://YOUR-APP.vercel.app`
  - `CSRF_TRUSTED_ORIGINS=https://YOURNAME.pythonanywhere.com`
  - `NUM_PROXIES=1` and your Gemini key and models
- Run `python manage.py migrate` and `python manage.py collectstatic --noinput`.
- In the **Web** tab: **Add a new web app** → **Manual configuration** → **Python 3.12**.
- Set **Virtualenv** to `/home/YOURNAME/ai-car-mechanic-chatbot/backend/venv`.
- Replace the **WSGI configuration file** content with:

  ```python
  import sys

  sys.path.insert(0, "/home/YOURNAME/ai-car-mechanic-chatbot/backend")

  from config.wsgi import application
  ```

- Add a **Static files** entry: URL `/static/` → `/home/YOURNAME/ai-car-mechanic-chatbot/backend/staticfiles`.
- Turn on **Force HTTPS**, click **Reload**, and check `https://YOURNAME.pythonanywhere.com/api/health/` shows `{"status": "ok"}`.
- To update: `git pull`, `python manage.py migrate`, `python manage.py collectstatic --noinput`, then **Reload**.
- Every 3 months, click **Run until 3 months from today** in the Web tab to keep the free app running.

**Frontend on Vercel**

- Import the GitHub repo in Vercel and set **Root Directory** to `frontend`.
- Add `NEXT_PUBLIC_API_URL=https://YOURNAME.pythonanywhere.com/api` and deploy.
- If you change this value later, redeploy, because it is fixed at build time.

**Notes**

- The free Gemini key has small daily limits and the models are sometimes busy. Enable billing for real users.
- There is no login, so chat history belongs to each browser.
