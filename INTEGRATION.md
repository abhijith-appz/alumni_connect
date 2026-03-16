# 🔗 How to Combine Frontend + Backend & Run

This guide walks you through merging the two downloaded zips into one working Django application.

---

## 📦 What You Have

| File                        | Contents                              |
|-----------------------------|---------------------------------------|
| `alumni_system_frontend.zip`| HTML templates + CSS + JavaScript     |
| `alumni_backend.zip`        | Django project (Python/backend)       |

---

## 🗂 Step 1 — Extract Both Zips

Create a single project folder and extract both zips into it:

```
your-project/
├── alumni_backend/        ← extract alumni_backend.zip here
└── alumni_system/         ← extract alumni_system_frontend.zip here
```

**On Windows:** Right-click each zip → "Extract All"
**On Mac/Linux:**
```bash
mkdir my-alumni-project
cd my-alumni-project
unzip ~/Downloads/alumni_backend.zip
unzip ~/Downloads/alumni_system_frontend.zip
```

---

## 📁 Step 2 — Copy Frontend Files into the Backend

The Django backend needs the HTML templates and CSS/JS files from the frontend zip.

### Copy Templates
```bash
# From inside my-alumni-project/
cp -r alumni_system/templates/*  alumni_backend/templates/
```

### Copy Static Files (CSS, JS)
```bash
cp -r alumni_system/static/*  alumni_backend/static/
```

After this, your `alumni_backend/` folder should look like:

```
alumni_backend/
├── manage.py
├── requirements.txt
├── .env.example
├── alumni_project/
├── apps/
├── templates/              ← HTML files are here now
│   ├── shared/
│   │   ├── base.html
│   │   ├── dashboard_base.html
│   │   ├── 404.html
│   │   ├── 403.html
│   │   ├── notifications.html
│   │   └── user_settings.html
│   ├── public/
│   │   ├── home.html
│   │   ├── about.html
│   │   ├── contact.html
│   │   ├── faq.html
│   │   └── alumni_directory.html
│   ├── auth/
│   │   ├── login.html
│   │   ├── register_student.html
│   │   ├── register_alumni.html
│   │   ├── forgot_password.html
│   │   └── reset_password.html
│   ├── student/
│   ├── alumni/
│   ├── ai/
│   └── admin/
└── static/                 ← CSS/JS are here now
    ├── css/
    │   ├── base.css
    │   ├── layout.css
    │   └── pages.css
    └── js/
        └── main.js
```

---

## 🐍 Step 3 — Set Up Python Environment

### 3a. Open a terminal inside `alumni_backend/`
```bash
cd alumni_backend
```

### 3b. Create a virtual environment
```bash
# Mac/Linux
python3 -m venv venv
source venv/bin/activate

# Windows (Command Prompt)
python -m venv venv
venv\Scripts\activate.bat

# Windows (PowerShell)
python -m venv venv
venv\Scripts\Activate.ps1
```

You should see `(venv)` at the start of your terminal prompt.

### 3c. Install all packages
```bash
pip install -r requirements.txt
```

This installs Django, REST framework, Pillow (images), Anthropic (AI), WhiteNoise (static files), and other dependencies.

---

## ⚙️ Step 4 — Configure Environment Variables

```bash
# Copy the example file
cp .env.example .env
```

Now open `.env` in any text editor and set these values:

```env
# Required
SECRET_KEY=any-long-random-string-at-least-50-chars

# For AI features (get free key at console.anthropic.com)
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here

# Leave these as-is for local development
DEBUG=True
ALLOWED_HOSTS=localhost 127.0.0.1
```

**How to generate a SECRET_KEY:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

---

## 🗄 Step 5 — Set Up the Database

```bash
# Create all database tables
python manage.py migrate
```

You'll see output like:
```
Applying accounts.0001_initial... OK
Applying alumni.0001_initial... OK
Applying jobs.0001_initial... OK
...
```

---

## 🌱 Step 6 — Add Demo Data (Recommended)

```bash
python manage.py seed_data
```

This creates ready-to-use demo accounts:

| Role    | Username  | Password  |
|---------|-----------|-----------|
| Admin   | admin     | admin123  |
| Alumni  | alumni1   | pass123   |
| Alumni  | alumni2   | pass123   |
| Student | student1  | pass123   |
| Student | student2  | pass123   |
| ...     | ...       | ...       |

It also creates 20 sample jobs, 5 events, and sample messages.

---

## 📁 Step 7 — Collect Static Files

```bash
python manage.py collectstatic --noinput
```

This copies all CSS/JS/images to `staticfiles/` so Django can serve them.

---

## 🚀 Step 8 — Run the Server

```bash
python manage.py runserver
```

Open your browser and go to: **http://localhost:8000**

---

## 🧭 Where to Go First

| What you want to see     | URL                                   | Login            |
|--------------------------|---------------------------------------|------------------|
| Home page (public)       | http://localhost:8000/                | No login needed  |
| Student login            | http://localhost:8000/auth/login/     | student1/pass123 |
| Student dashboard        | http://localhost:8000/student/dashboard/ | student1/pass123 |
| Alumni dashboard         | http://localhost:8000/alumni/dashboard/  | alumni1/pass123  |
| Admin dashboard          | http://localhost:8000/staff/dashboard/   | admin/admin123   |
| Django admin panel       | http://localhost:8000/admin/          | admin/admin123   |
| AI Chat                  | http://localhost:8000/ai/chat/        | any login        |
| Job Board                | http://localhost:8000/jobs/           | any login        |
| Events                   | http://localhost:8000/events/         | any login        |

---

## ❗ Troubleshooting

### "TemplateDoesNotExist" error
The HTML templates weren't copied correctly. Double-check step 2:
```bash
ls alumni_backend/templates/shared/base.html
# Should print the file path, not an error
```

### "No module named 'django'" error
The virtual environment isn't activated. Run:
```bash
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```

### Static files not loading (CSS broken)
Run collectstatic again:
```bash
python manage.py collectstatic --noinput
```
Or check that `DEBUG=True` in your `.env` — Django serves static files automatically in debug mode.

### "ANTHROPIC_API_KEY" warning in AI chat
The AI features need a key from [console.anthropic.com](https://console.anthropic.com). Everything else works without it — the AI chat will just show a "service not configured" message.

### Port 8000 already in use
```bash
python manage.py runserver 8080
# Then visit http://localhost:8080
```

### "ModuleNotFoundError" for any package
```bash
pip install -r requirements.txt
```

### Database errors after pulling updates
```bash
python manage.py migrate
```

---

## 🗂 Final Folder Structure (after integration)

```
alumni_backend/
├── manage.py                  ← Main Django entry point
├── requirements.txt           ← Python packages
├── .env                       ← Your configuration (SECRET_KEY, etc.)
├── db.sqlite3                 ← Database (created after migrate)
├── staticfiles/               ← Collected static files (auto-generated)
│
├── alumni_project/            ← Django project settings
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── apps/                      ← All Django apps
│   ├── accounts/              ← User model, auth, notifications
│   ├── students/              ← Student profiles & views
│   ├── alumni/                ← Alumni profiles, approval workflow
│   ├── jobs/                  ← Job board & applications
│   ├── events/                ← Events & registrations
│   ├── messaging/             ← Direct messages & contact form
│   ├── ai_assistant/          ← Anthropic AI integration
│   └── core/                  ← Public pages, admin, announcements
│
├── templates/                 ← HTML templates (from frontend zip)
│   ├── shared/
│   ├── public/
│   ├── auth/
│   ├── student/
│   ├── alumni/
│   ├── ai/
│   └── admin/
│
└── static/                    ← CSS/JS source (from frontend zip)
    ├── css/
    └── js/
```

---

## ⚡ Quick Automation (Mac/Linux only)

If you prefer, run the setup script which does steps 2–8 automatically:

```bash
cd alumni_backend
bash setup.sh
```

Then just run:
```bash
python manage.py runserver
```

---

## 🚢 Going to Production?

See the `Production Deployment` section in `README.md` for PostgreSQL, Gunicorn, and Nginx configuration.
