# AlumniConnect — Alumni Management System

> A full-stack web platform connecting students and alumni at Vast University through job boards, events, AI-powered career guidance, and direct messaging.

![Django](https://img.shields.io/badge/Django-5.x-green)
![Python](https://img.shields.io/badge/Python-3.14-blue)
![AI](https://img.shields.io/badge/AI-Groq%20Llama%203.3-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

## Features
- 🎓 **Student Portal** — Browse jobs, events, search alumni, AI career guidance
- 🏛️ **Alumni Portal** — Post jobs, message students, manage profile
- ⚙️ **Admin Panel** — Manage users, approve alumni, system reports
- 🤖 **AI Assistant** — Powered by Groq API (Llama 3.3 70B)
- 💬 **Real-time Messaging** — Direct chat between students and alumni
- 📅 **Events** — Register for on-campus, online, and hybrid events

## Tech Stack
| Layer | Technology |
|-------|-----------|
| Backend | Django 5.x, Python |
| Frontend | HTML5, CSS3, JavaScript (50 templates) |
| Database | SQLite / PostgreSQL |
| AI | Groq API — Llama 3.3 70B |
| API | Django REST Framework |

## Quick Start
```bash
git clone https://github.com/YOUR_USERNAME/alumniconnect.git
cd alumniconnect
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your SECRET_KEY
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

## Demo Logins
| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| Alumni | alumni1 | pass123 |
| Student | student1 | pass123 |

## Project Structure
```
alumni_backend/
├── apps/           # 8 Django apps
├── templates/      # 50 HTML templates
├── static/         # CSS + JS
└── alumni_project/ # Settings & URLs
```

---
Built for Vast  — 2026
