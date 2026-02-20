# Database & API Schema Documentation

## Database Schema (SQLAlchemy Models)

### User Model
```python
Table: users

Columns:
- username: String (Primary Key, Indexed)
- password: String (Hashed with bcrypt)

Purpose: Store user authentication credentials
```

### Message Model
```python
Table: messages

Columns:
- id: Integer (Primary Key, Auto-increment, Indexed)
- username: String (Foreign reference to User)
- text: String (Message content)

Purpose: Store chat message history
```

## API Schemas (Pydantic Models)

### 1. UserAuth
**Purpose:** User registration and login request

```python
{
  "username": "string",
  "password": "string"
}
```

**Example:**
```json
{
  "username": "john_doe",
  "password": "SecurePass123"
}
```

**Used in:**
- `POST /auth/register`
- `POST /auth/login`

---

### 2. Token
**Purpose:** Authentication response with JWT tokens

```python
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "string" (default: "bearer")
}
```

**Example:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**JWT Payload Structure:**
```json
{
  "sub": "username",
  "exp": 1234567890
}
```

**Token Expiration:**
- Access Token: 15 minutes
- Refresh Token: 7 days

**Used in:**
- `POST /auth/login` (response)
- `POST /auth/refresh` (response)

---

### 3. RefreshTokenRequest
**Purpose:** Request new access token using refresh token

```python
{
  "refresh_token": "string"
}
```

**Example:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Used in:**
- `POST /auth/refresh`

---

### 4. MessageResponse
**Purpose:** Chat message response

```python
{
  "id": "integer",
  "username": "string",
  "text": "string"
}
```

**Example:**
```json
{
  "id": 1,
  "username": "john_doe",
  "text": "Hello, everyone!"
}
```

**Used in:**
- `GET /auth/messages` (response - array of messages)

---

## API Endpoints Schema

### Authentication Endpoints

#### 1. Register User
```
POST /auth/register

Request Body: UserAuth
{
  "username": "string",
  "password": "string"
}

Response: 200 OK
{
  "message": "Registration successful"
}

Error Responses:
- 400: Username already exists
```

#### 2. Login User
```
POST /auth/login

Request Body: UserAuth
{
  "username": "string",
  "password": "string"
}

Response: 200 OK (Token)
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "bearer"
}

Error Responses:
- 401: Invalid username or password
```

#### 3. Refresh Token
```
POST /auth/refresh

Request Body: RefreshTokenRequest
{
  "refresh_token": "string"
}

Response: 200 OK (Token)
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "bearer"
}

Error Responses:
- 401: Invalid refresh token
```

#### 4. Get Messages (Protected)
```
GET /auth/messages

Headers:
Authorization: Bearer <access_token>

Response: 200 OK (Array of MessageResponse)
[
  {
    "id": 1,
    "username": "john_doe",
    "text": "Hello!"
  },
  {
    "id": 2,
    "username": "jane_smith",
    "text": "Hi there!"
  }
]

Error Responses:
- 401: Invalid or expired token
```

---

## WebSocket Schema

### WebSocket Connection
```
WS /ws?token=<access_token>

Query Parameters:
- token: JWT access token (required)

Connection Flow:
1. Client connects with valid access token
2. Server validates JWT token
3. If valid: Connection accepted
4. If invalid: Connection closed with code 1008

Message Format (Server → Client):
"username: message text"

Example:
"john_doe: Hello everyone!"

Message Format (Client → Server):
Plain text message

Example:
"Hello everyone!"
```

### WebSocket Events

#### Client → Server
```javascript
// Send message
ws.send("Hello everyone!");
```

#### Server → Client
```javascript
// Receive message
ws.onmessage = (event) => {
  // event.data = "username: message text"
  console.log(event.data);
};
```

#### Connection States
```javascript
ws.onopen = () => {
  // Connection established
};

ws.onerror = (error) => {
  // Connection error
};

ws.onclose = () => {
  // Connection closed
};
```

---

## Frontend LocalStorage Schema

### Stored Data
```javascript
localStorage.setItem('access_token', 'JWT_ACCESS_TOKEN');
localStorage.setItem('refresh_token', 'JWT_REFRESH_TOKEN');
```

### Data Structure
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

## Error Response Schema

### Standard Error Format
```json
{
  "detail": "Error message description"
}
```

### Common HTTP Status Codes
- `200 OK` - Success
- `400 Bad Request` - Invalid input (e.g., username exists)
- `401 Unauthorized` - Invalid credentials or expired token
- `404 Not Found` - Endpoint not found
- `500 Internal Server Error` - Server error

---

## Database Relationships

```
┌─────────────┐
│    users    │
├─────────────┤
│ username PK │◄─────┐
│ password    │      │
└─────────────┘      │
                     │
                     │ (Foreign Key)
                     │
┌─────────────┐      │
│  messages   │      │
├─────────────┤      │
│ id PK       │      │
│ username    │──────┘
│ text        │
└─────────────┘
```

---

## Security Schema

### Password Hashing
```
Algorithm: bcrypt
Salt Rounds: Auto-generated by bcrypt
Storage: Hashed password stored in database
```

### JWT Configuration
```python
SECRET_KEY: "your-secret-key-change-this-in-production"
ALGORITHM: "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: 15
REFRESH_TOKEN_EXPIRE_DAYS: 7
```

### Token Validation Flow
```
1. Client sends request with Bearer token
2. Server extracts token from Authorization header
3. Server decodes JWT using SECRET_KEY
4. Server validates expiration time
5. Server extracts username from "sub" claim
6. If valid: Process request
7. If invalid: Return 401 Unauthorized
```

---

## Complete Request/Response Examples

### Registration Flow
```bash
# Request
POST /auth/register
Content-Type: application/json

{
  "username": "alice",
  "password": "SecurePass123"
}

# Response
200 OK
{
  "message": "Registration successful"
}
```

### Login Flow
```bash
# Request
POST /auth/login
Content-Type: application/json

{
  "username": "alice",
  "password": "SecurePass123"
}

# Response
200 OK
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhbGljZSIsImV4cCI6MTcwOTU2NzgwMH0.xyz",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhbGljZSIsImV4cCI6MTcxMDE3MjYwMH0.abc",
  "token_type": "bearer"
}
```

### Get Messages Flow
```bash
# Request
GET /auth/messages
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Response
200 OK
[
  {
    "id": 1,
    "username": "alice",
    "text": "Hello!"
  },
  {
    "id": 2,
    "username": "bob",
    "text": "Hi Alice!"
  }
]
```

### WebSocket Chat Flow
```javascript
// Connect
const ws = new WebSocket('ws://localhost:8000/ws?token=ACCESS_TOKEN');

// Send message
ws.send("Hello everyone!");

// Receive message
ws.onmessage = (event) => {
  console.log(event.data); // "alice: Hello everyone!"
};
```

---

## Data Validation Rules

### Username
- Type: String
- Required: Yes
- Min Length: 1
- Max Length: Unlimited (recommended: 20)
- Unique: Yes

### Password
- Type: String
- Required: Yes
- Min Length: 1 (recommended: 8)
- Hashing: bcrypt
- Storage: Never stored in plain text

### Message Text
- Type: String
- Required: Yes
- Min Length: 1
- Max Length: Unlimited (recommended: 1000)

---

## Environment Configuration

### Required Settings
```python
SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7
DATABASE_URL = "sqlite+aiosqlite:///./chat.db"
```

### CORS Configuration
```python
allow_origins = ["*"]  # Change in production
allow_credentials = True
allow_methods = ["*"]
allow_headers = ["*"]
```
