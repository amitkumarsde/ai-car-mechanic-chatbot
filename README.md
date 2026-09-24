# AI Car Mechanic Chatbot

- A web chatbot where a car owner chats with a virtual senior mechanic.
- The bot asks follow-up questions, gives a diagnosis, suggests a repair and books a mechanic.
- Common problems are answered with normal backend rules. Google Gemini is used **only** when rules cannot help (unknown problems, photos, audio and video).

## Features

- Home page with common car problems that open the chat in one click
- Chat that only answers car questions and politely rejects other topics
- Follow-up questions before a diagnosis
- Upload photos, engine sounds (audio) and videos for AI analysis
- Diagnosis with problem, service, cost range and urgency
- "Book Mechanic" button after a diagnosis (one booking per diagnosis)
- Chat history, diagnosis history and booking details page
- Each reply shows "Instant answer" (rules) or "AI answer" (Gemini)

## Tech stack

- **Frontend:** Next.js 16, React 19, TypeScript, Tailwind CSS, Lucide React
- **Backend:** Python, Django 6, Django REST Framework
- **Database:** SQLite
- **AI:** Google Gemini (`google-genai`)
- **Hosting:** Vercel (frontend), AWS EC2 with nginx + gunicorn (backend)

## Project structure

```
ai-car-mechanic-chatbot/
├── backend/
│   ├── config/              Django settings and main URLs
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
│   ├── deploy/              Server setup, deploy, backup, nginx and gunicorn files
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   └── src/
│       ├── app/             Pages: / (home), /chat, /history, /booking/[id]
│       ├── components/      Header, footer, chat window, input, messages, diagnosis card, booking form, history
│       ├── hooks/useChat.ts Chat state and actions
│       └── lib/             API client, types, file checks, browser id
└── .github/workflows/ci.yml Runs tests on every push
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

- `DEBUG` - `True` on your computer, `False` on the server
- `DJANGO_SECRET_KEY` - long random secret (required when `DEBUG=False`)
- `ALLOWED_HOSTS` - domains that can reach the API, e.g. `localhost,127.0.0.1`
- `CORS_ALLOWED_ORIGINS` - frontend URL, e.g. `http://localhost:3000`
- `CSRF_TRUSTED_ORIGINS` - API URL with https (only needed for `/admin` on the server)
- `GEMINI_API_KEY` - your Gemini key
- `GEMINI_MODEL` - main model (default `gemini-3.5-flash-lite`)
- `GEMINI_FALLBACK_MODEL` - backup model when the main one is busy (default `gemini-3.1-flash-lite`)
- `SQLITE_PATH`, `MEDIA_ROOT`, `STATIC_ROOT` - leave empty locally; on the server use `/var/lib/carbot/...`
- `NUM_PROXIES` - `1` on the server (nginx in front), empty locally
- `SECURE_SSL_REDIRECT` - `True` once HTTPS works on the server

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

## Where data is saved

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

**Backend on AWS EC2 (free tier)**

- Launch an **Ubuntu 24.04** EC2 instance and open ports 22 (your IP), 80 and 443.
- Use EC2, not Lambda or Elastic Beanstalk, so the SQLite file and uploads stay on disk.
- Point a domain to the server IP (a free one from duckdns.org works). HTTPS needs a domain.
- Clone the repo to `/home/ubuntu/app` and create `backend/.env` with `DEBUG=False`, a new secret key, your domain in `ALLOWED_HOSTS`, your Vercel URL in `CORS_ALLOWED_ORIGINS`, `NUM_PROXIES=1`, `SECURE_SSL_REDIRECT=False`, and `SQLITE_PATH=/var/lib/carbot/db.sqlite3`, `MEDIA_ROOT=/var/lib/carbot/media`, `STATIC_ROOT=/var/lib/carbot/static`.
- Run `bash backend/deploy/setup_server.sh YOUR_DOMAIN`. It installs everything, creates the database, starts gunicorn and nginx, and adds a nightly database backup.
- Run `sudo certbot --nginx -d YOUR_DOMAIN` for free HTTPS, then set `SECURE_SSL_REDIRECT=True` and run `sudo systemctl restart gunicorn`.
- Check `https://YOUR_DOMAIN/api/health/` shows `{"status": "ok"}`.
- For later updates run `bash backend/deploy/deploy.sh` on the server.

**Frontend on Vercel**

- Import the GitHub repo in Vercel and set **Root Directory** to `frontend`.
- Add `NEXT_PUBLIC_API_URL=https://YOUR_DOMAIN/api` and deploy.
- If you change this value later, redeploy, because it is fixed at build time.

**Notes**

- The free Gemini key has small daily limits. Enable billing for real users.
- There is no login, so chat history belongs to each browser.
