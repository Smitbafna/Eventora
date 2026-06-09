# Eventora

Eventora is a full-stack event media management platform that enables organizations, clubs, photographers, and participants to create events, organize media into albums, and securely manage uploads with role-based access control.

Built using FastAPI, React, and TypeScript.

---

## Features

### Event Management
- Create and manage events
- Event categories, descriptions, and metadata
- Dedicated event pages

### Media Management
- Upload photos and videos
- Organize media into albums
- Browse media by event or album
- Media cards and previews

### Album System
- Create albums per event
- Group media logically
- Album-level browsing

### Authentication & Authorization
- JWT authentication
- Role-based access control
- Different permissions for different user roles

### User Roles

Supported roles include:

- Admin
- Photographer
- Club Member
- Viewer

Role permissions determine:

- Upload permissions
- Event management access
- Media management capabilities



---


# Architecture Overview

```

Frontend (React + TS)
↓
API Layer (Generated Client)
↓
FastAPI Backend
↓
Services / CRUD Layer
↓
Database (PostgreSQL)

```

---

# Getting Started

## Clone Repository

```bash
git clone <repo-url>

cd monorepo
```

---

# Backend Setup

Create virtual environment:

```bash
python -m venv .venv
```

Activate:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure environment variables:

```env
DATABASE_URL=
SECRET_KEY=
FIRST_SUPERUSER=
FIRST_SUPERUSER_PASSWORD=
```

Run migrations:

```bash
alembic upgrade head
```

Start backend:

```bash
uvicorn app.main:app --reload
```

Backend:

```
http://localhost:8000
```

---

# Frontend Setup

Install dependencies:

```bash
npm install
```

Start frontend:

```bash
npm run dev
```

Frontend:

```
http://localhost:5173
```

---

# Authentication Flow

```

Login
↓

JWT Token Generated
↓

Stored Client Side
↓

Authenticated Requests
↓

Protected Routes

```

---

# Media Flow

```

Create Event
↓

Create Album
↓

Upload Media
↓

Media Associated With Event
↓

View By Event / Album

```

---

# API Overview

## Authentication

```
POST /login/access-token
```

## Events

```
GET /events
POST /events
GET /events/{id}
```

## Albums

```
GET /albums
POST /albums
GET /albums/event/{id}
```

## Media

```
POST /media
GET /media/event/{id}
GET /media/album/{id}
```

---

# Development

Run backend:

```bash
uvicorn app.main:app --reload
```

Run frontend:

```bash
npm run dev
```

Generate migrations:

```bash
alembic revision --autogenerate -m "message"
```

Apply migrations:

```bash
alembic upgrade head
```

---

# License

MIT License

```
