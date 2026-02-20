from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# ============= AUTH SCHEMAS =============

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshTokenRequest(BaseModel):
    refresh_token: str

# ============= USER SCHEMAS =============

class UserProfile(BaseModel):
    id: int
    name: str
    email: str
    
    class Config:
        from_attributes = True

class UserListItem(BaseModel):
    id: int
    name: str
    email: str
    
    class Config:
        from_attributes = True

# ============= CONVERSATION SCHEMAS =============

class ConversationCreate(BaseModel):
    user2_id: int

class ConversationResponse(BaseModel):
    id: int
    user1: int
    user2: int
    last_message: Optional[str]
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ConversationWithUser(BaseModel):
    id: int
    other_user_id: int
    other_user_name: str
    other_user_email: str
    last_message: Optional[str]
    updated_at: datetime

# ============= MESSAGE SCHEMAS =============

class MessageCreate(BaseModel):
    text: str

class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    sender_id: int
    text: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class MessageWithSender(BaseModel):
    id: int
    conversation_id: int
    sender_id: int
    sender_name: str
    text: str
    created_at: datetime
    is_own: bool = False
