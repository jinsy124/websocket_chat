# WhatsApp-Like Chat API Endpoints

## 🔐 Authentication Endpoints

### 1. Register User
```http
POST /auth/register

Request Body:
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "SecurePass123"
}

Response: 200 OK
{
  "message": "Registration successful",
  "user_id": 1
}
```

### 2. Login
```http
POST /auth/login

Request Body:
{
  "email": "john@example.com",
  "password": "SecurePass123"
}

Response: 200 OK
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

### 3. Refresh Token
```http
POST /auth/refresh

Request Body:
{
  "refresh_token": "eyJhbGc..."
}

Response: 200 OK
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

---

## 👤 User Endpoints (Protected)

### 4. Get Current User Profile
```http
GET /users/me
Authorization: Bearer <access_token>

Response: 200 OK
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com"
}
```

### 5. Get All Users
```http
GET /users
Authorization: Bearer <access_token>

Response: 200 OK
[
  {
    "id": 2,
    "name": "Jane Smith",
    "email": "jane@example.com"
  },
  {
    "id": 3,
    "name": "Bob Wilson",
    "email": "bob@example.com"
  }
]

Purpose: Display list of users to start new conversations
```

---

## 💬 Conversation Endpoints (Protected)

### 6. Get All Conversations (HOME PAGE)
```http
GET /conversations
Authorization: Bearer <access_token>

Response: 200 OK
[
  {
    "id": 1,
    "other_user_id": 2,
    "other_user_name": "Jane Smith",
    "other_user_email": "jane@example.com",
    "last_message": "Hey, how are you?",
    "updated_at": "2024-02-18T10:30:00"
  },
  {
    "id": 2,
    "other_user_id": 3,
    "other_user_name": "Bob Wilson",
    "other_user_email": "bob@example.com",
    "last_message": "See you tomorrow!",
    "updated_at": "2024-02-18T09:15:00"
  }
]

Purpose: Display home page with all conversations (like WhatsApp chat list)
```

### 7. Create/Get Conversation
```http
POST /conversations
Authorization: Bearer <access_token>

Request Body:
{
  "user2_id": 2
}

Response: 200 OK
{
  "conversation_id": 1
}

Purpose: Start a new conversation or get existing one with a user
```

---

## 📨 Message Endpoints (Protected)

### 8. Get Messages in Conversation
```http
GET /conversations/{conversation_id}/messages
Authorization: Bearer <access_token>

Example: GET /conversations/1/messages

Response: 200 OK
[
  {
    "id": 1,
    "conversation_id": 1,
    "sender_id": 1,
    "sender_name": "John Doe",
    "text": "Hello!",
    "created_at": "2024-02-18T10:00:00",
    "is_own": true
  },
  {
    "id": 2,
    "conversation_id": 1,
    "sender_id": 2,
    "sender_name": "Jane Smith",
    "text": "Hi! How are you?",
    "created_at": "2024-02-18T10:01:00",
    "is_own": false
  }
]

Purpose: Display chat messages in a conversation
```

### 9. Send Message
```http
POST /conversations/{conversation_id}/messages
Authorization: Bearer <access_token>

Example: POST /conversations/1/messages

Request Body:
{
  "text": "Hello! How are you?"
}

Response: 200 OK
{
  "id": 3,
  "conversation_id": 1,
  "sender_id": 1,
  "text": "Hello! How are you?",
  "created_at": "2024-02-18T10:30:00"
}

Purpose: Send a message in a conversation
```

---

## 🔌 WebSocket Endpoint

### 10. Real-time Chat WebSocket
```javascript
WS /ws?token=<access_token>&conversation_id=<conversation_id>

// Connect
const ws = new WebSocket('ws://localhost:8000/ws?token=ACCESS_TOKEN&conversation_id=1');

// Send message
ws.send(JSON.stringify({
  "text": "Hello in real-time!"
}));

// Receive message
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log(message);
  // {
  //   "sender_id": 2,
  //   "sender_name": "Jane Smith",
  //   "text": "Hi there!",
  //   "created_at": "2024-02-18T10:30:00"
  // }
};

Purpose: Real-time message delivery in active conversation
```

---

## 📱 Frontend Flow

### Login/Register Flow
```
1. User opens app
2. Shows login/register screen
3. User registers: POST /auth/register
4. User logs in: POST /auth/login
5. Store tokens in localStorage
6. Redirect to home page
```

### Home Page Flow
```
1. User logged in
2. Call: GET /conversations
3. Display list of conversations with:
   - Other user's name
   - Last message preview
   - Timestamp
4. User clicks on a conversation
5. Navigate to chat page
```

### Chat Page Flow
```
1. User opens conversation
2. Call: GET /conversations/{id}/messages
3. Display all messages
4. Connect WebSocket for real-time updates
5. User types and sends message
6. Call: POST /conversations/{id}/messages
7. Message appears in real-time via WebSocket
```

### Start New Chat Flow
```
1. User clicks "New Chat" button
2. Call: GET /users (get all users)
3. Display user list
4. User selects a user
5. Call: POST /conversations with user2_id
6. Get conversation_id
7. Navigate to chat page with that conversation_id
```

---

## 🗄️ Database Schema

```
users
├── id (PK)
├── name
├── email (unique)
└── password (hashed)

conversations
├── id (PK)
├── user1 (FK → users.id)
├── user2 (FK → users.id)
├── last_message
└── updated_at

messages
├── id (PK)
├── conversation_id (FK → conversations.id)
├── sender_id (FK → users.id)
├── text
└── created_at
```

---

## 🎯 Complete User Journey

### First Time User
1. **Register**: `POST /auth/register`
2. **Login**: `POST /auth/login` → Get tokens
3. **Home Page**: `GET /conversations` → Empty list
4. **New Chat**: `GET /users` → See all users
5. **Select User**: `POST /conversations` → Create conversation
6. **Chat**: `GET /conversations/{id}/messages` → Start chatting

### Returning User
1. **Auto Login**: Check localStorage for tokens
2. **Refresh Token**: `POST /auth/refresh` (if access token expired)
3. **Home Page**: `GET /conversations` → See all chats
4. **Open Chat**: Click conversation → Load messages
5. **Real-time**: WebSocket connection for live updates

---

## 🔒 Security

- All endpoints except `/auth/register` and `/auth/login` require Bearer token
- Passwords hashed with bcrypt
- JWT tokens with expiration
- Users can only access their own conversations
- WebSocket requires valid token

---

## 📊 Response Codes

- `200 OK` - Success
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - Invalid/expired token
- `403 Forbidden` - Not authorized for this resource
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error
