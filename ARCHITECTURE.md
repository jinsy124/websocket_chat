# System Architecture

## Project Structure
```
websocket_chat/
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI app & router configuration
│   ├── database.py          # Database engine & session
│   ├── models.py            # SQLAlchemy ORM models
│   ├── schemas.py           # Pydantic validation schemas
│   ├── utility.py           # JWT & password utilities
│   ├── services.py          # Business logic layer
│   ├── dependencies.py      # FastAPI dependencies
│   ├── index.html           # Frontend SPA
│   └── routes/
│       ├── __init__.py
│       ├── auth.py          # Auth & message endpoints
│       └── websocket.py     # WebSocket endpoint
├── venv/                    # Virtual environment
├── chat.db                  # SQLite database
├── README.md
├── SCHEMA.md
└── ARCHITECTURE.md
```

## System Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         FRONTEND                            │
│                      (index.html)                           │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   Login/     │  │   Chat UI    │  │  WebSocket   │    │
│  │   Register   │  │   Messages   │  │  Connection  │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│         │                  │                  │            │
│         │ HTTP             │ HTTP             │ WS         │
└─────────┼──────────────────┼──────────────────┼────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                         BACKEND                             │
│                      (FastAPI)                              │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                    main.py                           │  │
│  │  - CORS Middleware                                   │  │
│  │  - Router Registration                               │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                  │
│         ┌────────────────┼────────────────┐               │
│         │                │                │               │
│         ▼                ▼                ▼               │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐           │
│  │  auth.py │    │  chat.py │    │websocket │           │
│  │          │    │ (merged) │    │   .py    │           │
│  │ /register│    │          │    │   /ws    │           │
│  │ /login   │    │          │    │          │           │
│  │ /refresh │    │          │    │          │           │
│  │ /messages│    │          │    │          │           │
│  └──────────┘    └──────────┘    └──────────┘           │
│         │                              │                  │
│         ▼                              ▼                  │
│  ┌──────────────────┐         ┌──────────────────┐      │
│  │   services.py    │         │ dependencies.py  │      │
│  │                  │         │                  │      │
│  │ - register_user  │         │ - get_current_   │      │
│  │ - login_user     │         │   user           │      │
│  │ - refresh_token  │         │ - JWT validation │      │
│  │ - get_messages   │         └──────────────────┘      │
│  └──────────────────┘                  │                 │
│         │                              │                 │
│         ▼                              ▼                 │
│  ┌──────────────────┐         ┌──────────────────┐      │
│  │   utility.py     │         │   schemas.py     │      │
│  │                  │         │                  │      │
│  │ - hash_password  │         │ - UserAuth       │      │
│  │ - verify_password│         │ - Token          │      │
│  │ - create_token   │         │ - MessageResponse│      │
│  │ - verify_token   │         └──────────────────┘      │
│  └──────────────────┘                                    │
│         │                                                │
│         ▼                                                │
│  ┌──────────────────────────────────────────────────┐   │
│  │              database.py                         │   │
│  │  - Engine (SQLAlchemy)                          │   │
│  │  - SessionLocal (Async)                         │   │
│  │  - get_db() dependency                          │   │
│  └──────────────────────────────────────────────────┘   │
│         │                                                │
│         ▼                                                │
│  ┌──────────────────────────────────────────────────┐   │
│  │              models.py                           │   │
│  │  - User (username, password)                    │   │
│  │  - Message (id, username, text)                 │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                       DATABASE                              │
│                    (SQLite - chat.db)                       │
│                                                             │
│  ┌──────────────┐              ┌──────────────┐           │
│  │    users     │              │   messages   │           │
│  ├──────────────┤              ├──────────────┤           │
│  │ username PK  │◄─────────────│ id PK        │           │
│  │ password     │              │ username FK  │           │
│  └──────────────┘              │ text         │           │
│                                └──────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

## Authentication Flow

```
┌──────────┐                                    ┌──────────┐
│  Client  │                                    │  Server  │
└────┬─────┘                                    └────┬─────┘
     │                                               │
     │  1. POST /auth/register                      │
     │  { username, password }                      │
     ├──────────────────────────────────────────────►
     │                                               │
     │                    2. Hash password (bcrypt)  │
     │                    3. Store in database       │
     │                                               │
     │  4. { message: "Registration successful" }   │
     ◄──────────────────────────────────────────────┤
     │                                               │
     │  5. POST /auth/login                         │
     │  { username, password }                      │
     ├──────────────────────────────────────────────►
     │                                               │
     │                    6. Verify password         │
     │                    7. Create JWT tokens       │
     │                                               │
     │  8. { access_token, refresh_token }          │
     ◄──────────────────────────────────────────────┤
     │                                               │
     │  9. Store tokens in localStorage              │
     │                                               │
     │  10. GET /auth/messages                      │
     │  Authorization: Bearer <access_token>        │
     ├──────────────────────────────────────────────►
     │                                               │
     │                    11. Verify JWT             │
     │                    12. Query database         │
     │                                               │
     │  13. [ { id, username, text }, ... ]         │
     ◄──────────────────────────────────────────────┤
     │                                               │
```

## WebSocket Communication Flow

```
┌──────────┐                                    ┌──────────┐
│  Client  │                                    │  Server  │
└────┬─────┘                                    └────┬─────┘
     │                                               │
     │  1. WS /ws?token=<access_token>              │
     ├──────────────────────────────────────────────►
     │                                               │
     │                    2. Verify JWT token        │
     │                    3. Accept connection       │
     │                    4. Add to connections{}    │
     │                                               │
     │  5. Connection established                    │
     ◄──────────────────────────────────────────────┤
     │                                               │
     │  6. Send message: "Hello!"                   │
     ├──────────────────────────────────────────────►
     │                                               │
     │                    7. Save to database        │
     │                    8. Broadcast to all        │
     │                                               │
     │  9. Receive: "username: Hello!"              │
     ◄──────────────────────────────────────────────┤
     │                                               │
     │  10. Display in UI                           │
     │                                               │
```

## Token Refresh Flow

```
┌──────────┐                                    ┌──────────┐
│  Client  │                                    │  Server  │
└────┬─────┘                                    └────┬─────┘
     │                                               │
     │  1. Request with expired access_token        │
     ├──────────────────────────────────────────────►
     │                                               │
     │  2. 401 Unauthorized                         │
     ◄──────────────────────────────────────────────┤
     │                                               │
     │  3. POST /auth/refresh                       │
     │  { refresh_token }                           │
     ├──────────────────────────────────────────────►
     │                                               │
     │                    4. Verify refresh_token    │
     │                    5. Create new tokens       │
     │                                               │
     │  6. { access_token, refresh_token }          │
     ◄──────────────────────────────────────────────┤
     │                                               │
     │  7. Update localStorage                      │
     │  8. Retry original request                   │
     │                                               │
```

## Data Flow Layers

```
┌─────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                   │
│                      (index.html)                       │
│  - User Interface                                       │
│  - Event Handling                                       │
│  - LocalStorage Management                              │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                      API LAYER                          │
│                   (routes/*.py)                         │
│  - Request Validation                                   │
│  - Response Formatting                                  │
│  - Dependency Injection                                 │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   BUSINESS LOGIC LAYER                  │
│                    (services.py)                        │
│  - User Registration                                    │
│  - User Authentication                                  │
│  - Token Management                                     │
│  - Message Retrieval                                    │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                    UTILITY LAYER                        │
│                    (utility.py)                         │
│  - Password Hashing                                     │
│  - JWT Creation/Verification                            │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   DATA ACCESS LAYER                     │
│                 (database.py, models.py)                │
│  - Database Connection                                  │
│  - ORM Models                                           │
│  - Session Management                                   │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                    DATABASE LAYER                       │
│                    (SQLite - chat.db)                   │
│  - Data Persistence                                     │
│  - Query Execution                                      │
└─────────────────────────────────────────────────────────┘
```

## Security Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    SECURITY LAYERS                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. CORS Middleware                                     │
│     - Origin validation                                 │
│     - Credential handling                               │
│                                                         │
│  2. JWT Authentication                                  │
│     - Token validation                                  │
│     - Expiration checking                               │
│     - Signature verification                            │
│                                                         │
│  3. Password Security                                   │
│     - bcrypt hashing                                    │
│     - Salt generation                                   │
│     - No plain text storage                             │
│                                                         │
│  4. WebSocket Security                                  │
│     - Token-based authentication                        │
│     - Connection validation                             │
│                                                         │
│  5. Input Validation                                    │
│     - Pydantic schemas                                  │
│     - Type checking                                     │
│     - XSS prevention (HTML escaping)                    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    PRODUCTION SETUP                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Frontend: Static HTML/JS/CSS                           │
│  ├─ Served by FastAPI                                   │
│  └─ Can be deployed to CDN                              │
│                                                         │
│  Backend: FastAPI + Uvicorn                             │
│  ├─ ASGI Server                                         │
│  ├─ Async/Await support                                 │
│  └─ WebSocket support                                   │
│                                                         │
│  Database: SQLite (Development)                         │
│  └─ Can be replaced with PostgreSQL/MySQL               │
│                                                         │
│  Recommended Production Stack:                          │
│  ├─ Nginx (Reverse Proxy)                               │
│  ├─ Uvicorn (ASGI Server)                               │
│  ├─ PostgreSQL (Database)                               │
│  └─ Redis (Session/Cache - optional)                    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```
