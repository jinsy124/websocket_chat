from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas import (
    UserRegister, UserLogin, Token, RefreshTokenRequest,
    UserProfile, UserListItem, ConversationWithUser,
    ConversationCreate, MessageResponse, MessageCreate,
    MessageWithSender
)
from src.services import (
    register_user, login_user, refresh_user_token,
    get_current_user_profile, get_all_users,
    get_or_create_conversation, get_user_conversations,
    get_conversation_messages, send_message
)
from src.database import get_db
from src.dependencies import get_current_user_id
from typing import List

router = APIRouter(tags=["API"])

# ============= AUTH ENDPOINTS =============


@router.post("/auth/register")
async def register(user: UserRegister, db: AsyncSession = Depends(get_db)):
    """Register a new user"""
    return await register_user(user, db)


@router.post("/auth/login", response_model=Token)
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    """Login and get JWT tokens"""
    return await login_user(user, db)


@router.post("/auth/refresh", response_model=Token)
async def refresh(req: RefreshTokenRequest):
    """Refresh access token"""
    return await refresh_user_token(req.refresh_token)


@router.post("/auth/logout")
async def logout(current_user_id: int = Depends(get_current_user_id)):
    """Logout user (Client should discard the token)"""
    return {"message": "Successfully logged out"}

# ============= USER ENDPOINTS =============


@router.get("/users/me", response_model=UserProfile)
async def get_me(
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get current user profile"""
    return await get_current_user_profile(current_user_id, db)


@router.get("/users", response_model=List[UserListItem])
async def list_users(
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get all users (for starting new conversations)"""
    return await get_all_users(current_user_id, db)

# ============= CONVERSATION ENDPOINTS =============


@router.get("/conversations", response_model=List[ConversationWithUser])
async def get_conversations(
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get all conversations for current user (Home page)"""
    return await get_user_conversations(current_user_id, db)


@router.post("/conversations")
async def create_conversation(
    data: ConversationCreate,
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Create or get existing conversation with another user"""
    conversation = await get_or_create_conversation(current_user_id, data.user2_id, db)
    return {"conversation_id": conversation.id}

# ============= MESSAGE ENDPOINTS =============


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageWithSender])
async def get_messages(
    conversation_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get all messages in a conversation"""
    return await get_conversation_messages(conversation_id, current_user_id, db)


@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse)
async def create_message(
    conversation_id: int,
    message: MessageCreate,
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Send a message in a conversation"""
    return await send_message(conversation_id, current_user_id, message.text, db)
