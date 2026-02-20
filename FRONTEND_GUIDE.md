# Frontend Development Guide - WhatsApp-Like Chat

## 🎯 Backend Structure Overview

### Database Schema
```
users
├── id (Primary Key)
├── name
├── email (unique)
└── password (hashed)

conversations
├── id (Primary Key)
├── user1 (Foreign Key → users.id)
├── user2 (Foreign Key → users.id)
├── last_message
└── updated_at

messages
├── id (Primary Key)
├── conversation_id (Foreign Key → conversations.id)
├── sender_id (Foreign Key → users.id)
├── text
└── created_at
```

### API Endpoints Summary

**Base URL:** `http://localhost:8000`

| Method | Endpoint | Auth Required | Purpose |
|--------|----------|---------------|---------|
| POST | `/auth/register` | ❌ | Register new user |
| POST | `/auth/login` | ❌ | Login & get tokens |
| POST | `/auth/refresh` | ❌ | Refresh access token |
| GET | `/users/me` | ✅ | Get current user profile |
| GET | `/users` | ✅ | Get all users list |
| GET | `/conversations` | ✅ | Get all conversations (HOME) |
| POST | `/conversations` | ✅ | Create/get conversation |
| GET | `/conversations/{id}/messages` | ✅ | Get messages in chat |
| POST | `/conversations/{id}/messages` | ✅ | Send message |
| WS | `/ws` | ✅ | Real-time messaging |

---

## 📱 Frontend Pages Structure

### 1. Authentication Pages

#### Login Page (`/login`)
```
┌─────────────────────────────────┐
│         WhatsApp Clone          │
├─────────────────────────────────┤
│                                 │
│   Email:    [____________]      │
│   Password: [____________]      │
│                                 │
│   [      Login Button      ]    │
│   [   Register Button      ]    │
│                                 │
└─────────────────────────────────┘
```

**API Call:**
```javascript
POST /auth/login
Body: { email, password }
Response: { access_token, refresh_token, token_type }
```

**What to do:**
1. User enters email & password
2. Call login API
3. Store tokens in localStorage
4. Redirect to home page

---

#### Register Page (`/register`)
```
┌─────────────────────────────────┐
│         Create Account          │
├─────────────────────────────────┤
│                                 │
│   Name:     [____________]      │
│   Email:    [____________]      │
│   Password: [____________]      │
│                                 │
│   [    Register Button     ]    │
│   [Already have account?]       │
│                                 │
└─────────────────────────────────┘
```

**API Call:**
```javascript
POST /auth/register
Body: { name, email, password }
Response: { message, user_id }
```

**What to do:**
1. User enters name, email, password
2. Call register API
3. Show success message
4. Redirect to login page

---

### 2. Home Page (`/home` or `/`)

```
┌─────────────────────────────────────────┐
│  ☰  WhatsApp Clone        [Profile] 🔍  │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ 👤 Jane Smith                   │   │
│  │    Hey, how are you?            │   │
│  │    10:30 AM                     │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ 👤 Bob Wilson                   │   │
│  │    See you tomorrow!            │   │
│  │    Yesterday                    │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ 👤 Alice Johnson                │   │
│  │    Thanks!                      │   │
│  │    2 days ago                   │   │
│  └─────────────────────────────────┘   │
│                                         │
│                                         │
│                    [+ New Chat]         │
└─────────────────────────────────────────┘
```

**API Call:**
```javascript
GET /conversations
Headers: { Authorization: "Bearer <access_token>" }
Response: [
  {
    id: 1,
    other_user_id: 2,
    other_user_name: "Jane Smith",
    other_user_email: "jane@example.com",
    last_message: "Hey, how are you?",
    updated_at: "2024-02-19T10:30:00"
  },
  ...
]
```

**What to display:**
- List of all conversations
- Each item shows:
  - Other user's name
  - Last message preview (truncated)
  - Timestamp (formatted: "10:30 AM", "Yesterday", "2 days ago")
- Click on conversation → Navigate to chat page
- "New Chat" button → Navigate to users list

---

### 3. Users List Page (`/users`)

```
┌─────────────────────────────────────────┐
│  ←  Select User to Chat                 │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ 👤 Jane Smith                   │   │
│  │    jane@example.com             │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ 👤 Bob Wilson                   │   │
│  │    bob@example.com              │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ 👤 Alice Johnson                │   │
│  │    alice@example.com            │   │
│  └─────────────────────────────────┘   │
│                                         │
└─────────────────────────────────────────┘
```

**API Call:**
```javascript
GET /users
Headers: { Authorization: "Bearer <access_token>" }
Response: [
  {
    id: 2,
    name: "Jane Smith",
    email: "jane@example.com"
  },
  ...
]
```

**What to do:**
1. Display all users (except current user)
2. User clicks on a user
3. Call create conversation API
4. Navigate to chat page with conversation_id

**Create Conversation:**
```javascript
POST /conversations
Headers: { Authorization: "Bearer <access_token>" }
Body: { user2_id: 2 }
Response: { conversation_id: 1 }
```

---

### 4. Chat Page (`/chat/:conversationId`)

```
┌─────────────────────────────────────────┐
│  ←  Jane Smith                    ⋮     │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────────────┐               │
│  │ Hi! How are you?    │ Jane          │
│  │ 10:00 AM            │               │
│  └─────────────────────┘               │
│                                         │
│               ┌─────────────────────┐  │
│          You  │ I'm good, thanks!   │  │
│               │ 10:01 AM            │  │
│               └─────────────────────┘  │
│                                         │
│  ┌─────────────────────┐               │
│  │ What are you doing? │ Jane          │
│  │ 10:02 AM            │               │
│  └─────────────────────┘               │
│                                         │
│               ┌─────────────────────┐  │
│          You  │ Working on a project│  │
│               │ 10:03 AM            │  │
│               └─────────────────────┘  │
│                                         │
├─────────────────────────────────────────┤
│  [Type a message...]            [Send]  │
└─────────────────────────────────────────┘
```

**API Calls:**

**1. Load Messages:**
```javascript
GET /conversations/{conversation_id}/messages
Headers: { Authorization: "Bearer <access_token>" }
Response: [
  {
    id: 1,
    conversation_id: 1,
    sender_id: 2,
    sender_name: "Jane Smith",
    text: "Hi! How are you?",
    created_at: "2024-02-19T10:00:00",
    is_own: false
  },
  {
    id: 2,
    conversation_id: 1,
    sender_id: 1,
    sender_name: "You",
    text: "I'm good, thanks!",
    created_at: "2024-02-19T10:01:00",
    is_own: true
  },
  ...
]
```

**2. Send Message:**
```javascript
POST /conversations/{conversation_id}/messages
Headers: { Authorization: "Bearer <access_token>" }
Body: { text: "Hello!" }
Response: {
  id: 3,
  conversation_id: 1,
  sender_id: 1,
  text: "Hello!",
  created_at: "2024-02-19T10:05:00"
}
```

**3. Real-time Updates (WebSocket):**
```javascript
const ws = new WebSocket(
  `ws://localhost:8000/ws?token=${access_token}&conversation_id=${conversation_id}`
);

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  // Add message to chat UI
  displayMessage(message);
};
```

**What to display:**
- Messages in chronological order
- Own messages on right (blue background)
- Other user's messages on left (gray background)
- Sender name and timestamp
- Auto-scroll to bottom
- Input box at bottom

---

## 🔐 Authentication Flow

### Token Management

**Store tokens after login:**
```javascript
localStorage.setItem('access_token', data.access_token);
localStorage.setItem('refresh_token', data.refresh_token);
```

**Add token to requests:**
```javascript
const headers = {
  'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
  'Content-Type': 'application/json'
};
```

**Handle token expiration:**
```javascript
// If API returns 401
if (response.status === 401) {
  // Try to refresh token
  const refreshToken = localStorage.getItem('refresh_token');
  
  const refreshResponse = await fetch('/auth/refresh', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refreshToken })
  });
  
  if (refreshResponse.ok) {
    const data = await refreshResponse.json();
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    // Retry original request
  } else {
    // Redirect to login
    localStorage.clear();
    window.location.href = '/login';
  }
}
```

---

## 🎨 UI Components Needed

### 1. ConversationListItem
```jsx
<div className="conversation-item" onClick={() => openChat(conversation.id)}>
  <div className="avatar">👤</div>
  <div className="info">
    <div className="name">{conversation.other_user_name}</div>
    <div className="last-message">{conversation.last_message}</div>
  </div>
  <div className="time">{formatTime(conversation.updated_at)}</div>
</div>
```

### 2. MessageBubble
```jsx
<div className={`message ${message.is_own ? 'own' : 'other'}`}>
  <div className="sender">{message.sender_name}</div>
  <div className="text">{message.text}</div>
  <div className="time">{formatTime(message.created_at)}</div>
</div>
```

### 3. UserListItem
```jsx
<div className="user-item" onClick={() => startChat(user.id)}>
  <div className="avatar">👤</div>
  <div className="info">
    <div className="name">{user.name}</div>
    <div className="email">{user.email}</div>
  </div>
</div>
```

---

## 📝 Sample Frontend Prompt

**For React/Next.js:**
```
Create a WhatsApp-like chat application frontend using React/Next.js with the following:

1. Pages:
   - Login page with email and password fields
   - Register page with name, email, and password fields
   - Home page showing list of conversations
   - Users list page to start new chats
   - Chat page with message history and input

2. Features:
   - JWT authentication with token refresh
   - Real-time messaging using WebSocket
   - Responsive design (mobile-first)
   - Auto-scroll to latest messages
   - Timestamp formatting (relative time)
   - Loading states and error handling

3. API Integration:
   - Base URL: http://localhost:8000
   - Endpoints: /auth/login, /auth/register, /conversations, /users, /messages
   - WebSocket: ws://localhost:8000/ws

4. State Management:
   - User authentication state
   - Conversations list
   - Current chat messages
   - WebSocket connection

5. Styling:
   - Use Tailwind CSS
   - WhatsApp-like color scheme (green/white/gray)
   - Message bubbles (blue for own, gray for others)
   - Smooth animations

Please create the complete frontend with all components and pages.
```

**For Vue.js:**
```
Build a WhatsApp-style chat application using Vue 3 with Composition API:

[Same requirements as above, but specify Vue 3, Pinia for state management, Vue Router for navigation]
```

**For Plain HTML/JS:**
```
Create a WhatsApp-like chat application using vanilla JavaScript:

[Same requirements, but specify no frameworks, use fetch API, localStorage for state]
```

---

## 🚀 Quick Start Checklist

- [ ] Create login page
- [ ] Create register page
- [ ] Implement token storage
- [ ] Create home page (conversations list)
- [ ] Implement conversation click → navigate to chat
- [ ] Create users list page
- [ ] Implement start new chat flow
- [ ] Create chat page
- [ ] Load and display messages
- [ ] Implement send message
- [ ] Add WebSocket for real-time updates
- [ ] Add token refresh logic
- [ ] Add loading states
- [ ] Add error handling
- [ ] Style with responsive design

---

## 🔧 Testing the Backend

**Test with cURL or Postman:**

1. Register:
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"John","email":"john@test.com","password":"pass123"}'
```

2. Login:
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"john@test.com","password":"pass123"}'
```

3. Get Conversations:
```bash
curl http://localhost:8000/conversations \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 📚 Additional Resources

- API Documentation: See `API_ENDPOINTS.md`
- Architecture: See `ARCHITECTURE.md`
- Database Schema: See `SCHEMA.md`

---

## 💡 Tips

1. **Start Simple**: Build login → home → chat flow first
2. **Test Each Step**: Test API calls before building UI
3. **Use DevTools**: Check Network tab for API responses
4. **Handle Errors**: Always show user-friendly error messages
5. **Mobile First**: Design for mobile, then scale up
6. **Real-time Last**: Get basic chat working before adding WebSocket
