from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from fastapi import HTTPException
from src.models import User, Conversation, Message
from src.schemas import (
    UserRegister, UserLogin, Token, UserProfile,
    ConversationWithUser, MessageWithSender
)
from src.utility import hash_password, verify_password, create_access_token, create_refresh_token, verify_token

# ============= AUTH SERVICES =============


async def register_user(user: UserRegister, db: AsyncSession):
    """Register a new user"""
    try:
        # Check if email already exists
        result = await db.execute(select(User).where(User.email == user.email))
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise HTTPException(
                status_code=400, detail="Email already registered")

        # Hash password and create user
        hashed_pwd = hash_password(user.password)
        new_user = User(
            name=user.name,
            email=user.email,
            password=hashed_pwd
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return {"message": "Registration successful", "user_id": new_user.id}
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        await db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Registration failed: {str(e)}")


async def login_user(user: UserLogin, db: AsyncSession) -> Token:
    """Login user and return JWT tokens"""
    result = await db.execute(select(User).where(User.email == user.email))
    db_user = result.scalar_one_or_none()

    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(
            status_code=401, detail="Invalid email or password")

    # Create tokens with user_id in payload
    access_token = create_access_token(
        {"sub": str(db_user.id), "email": db_user.email})
    refresh_token = create_refresh_token(
        {"sub": str(db_user.id), "email": db_user.email})

    return Token(access_token=access_token, refresh_token=refresh_token)


async def refresh_user_token(refresh_token: str) -> Token:
    """Refresh access token using refresh token"""
    try:
        payload = verify_token(refresh_token)
        user_id = payload.get("sub")
        email = payload.get("email")
    except HTTPException:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    new_access_token = create_access_token({"sub": user_id, "email": email})
    new_refresh_token = create_refresh_token({"sub": user_id, "email": email})

    return Token(access_token=new_access_token, refresh_token=new_refresh_token)

# ============= USER SERVICES =============


async def get_current_user_profile(user_id: int, db: AsyncSession) -> UserProfile:
    """Get current user's profile"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserProfile.from_orm(user)


async def get_all_users(current_user_id: int, db: AsyncSession):
    """Get all users except current user"""
    result = await db.execute(select(User).where(User.id != current_user_id))
    users = result.scalars().all()
    return users

# ============= CONVERSATION SERVICES =============


async def get_or_create_conversation(user1_id: int, user2_id: int, db: AsyncSession):
    """Get existing conversation or create new one"""
    # Check if conversation already exists (in either direction)
    result = await db.execute(
        select(Conversation).where(
            or_(
                and_(Conversation.user1 == user1_id,
                     Conversation.user2 == user2_id),
                and_(Conversation.user1 == user2_id,
                     Conversation.user2 == user1_id)
            )
        )
    )
    conversation = result.scalar_one_or_none()

    if conversation:
        return conversation

    # Create new conversation
    new_conversation = Conversation(user1=user1_id, user2=user2_id)
    db.add(new_conversation)
    await db.commit()
    await db.refresh(new_conversation)

    return new_conversation


async def get_user_conversations(user_id: int, db: AsyncSession):
    """Get all conversations for a user with other user details"""
    result = await db.execute(
        select(Conversation).where(
            or_(Conversation.user1 == user_id, Conversation.user2 == user_id)
        ).order_by(Conversation.updated_at.desc())
    )
    conversations = result.scalars().all()

    # Get other user details for each conversation
    conversation_list = []
    for conv in conversations:
        other_user_id = conv.user2 if conv.user1 == user_id else conv.user1

        # Get other user details
        user_result = await db.execute(select(User).where(User.id == other_user_id))
        other_user = user_result.scalar_one_or_none()

        if other_user:
            conversation_list.append(
                ConversationWithUser(
                    id=conv.id,
                    other_user_id=other_user.id,
                    other_user_name=other_user.name,
                    other_user_email=other_user.email,
                    last_message=conv.last_message,
                    updated_at=conv.updated_at
                )
            )

    return conversation_list

# ============= MESSAGE SERVICES =============


async def get_conversation_messages(conversation_id: int, current_user_id: int, db: AsyncSession):
    """Get all messages in a conversation"""
    # Verify user is part of conversation
    result = await db.execute(select(Conversation).where(Conversation.id == conversation_id))
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if conversation.user1 != current_user_id and conversation.user2 != current_user_id:
        raise HTTPException(
            status_code=403, detail="Not authorized to view this conversation")

    # Get messages
    messages_result = await db.execute(
        select(Message).where(Message.conversation_id ==
                              conversation_id).order_by(Message.created_at)
    )
    messages = messages_result.scalars().all()

    # Get sender details for each message
    message_list = []
    for msg in messages:
        sender_result = await db.execute(select(User).where(User.id == msg.sender_id))
        sender = sender_result.scalar_one_or_none()

        if sender:
            message_list.append(
                MessageWithSender(
                    id=msg.id,
                    conversation_id=msg.conversation_id,
                    sender_id=msg.sender_id,
                    sender_name=sender.name,
                    text=msg.text,
                    created_at=msg.created_at,
                    is_own=(msg.sender_id == current_user_id)
                )
            )

    return message_list


async def send_message(conversation_id: int, sender_id: int, text: str, db: AsyncSession):
    """Send a message in a conversation"""
    # Verify conversation exists and user is part of it
    result = await db.execute(select(Conversation).where(Conversation.id == conversation_id))
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if conversation.user1 != sender_id and conversation.user2 != sender_id:
        raise HTTPException(
            status_code=403, detail="Not authorized to send messages in this conversation")

    # Create message
    new_message = Message(
        conversation_id=conversation_id,
        sender_id=sender_id,
        text=text
    )
    db.add(new_message)

    # Update conversation's last message
    conversation.last_message = text[:50] + "..." if len(text) > 50 else text

    await db.commit()
    await db.refresh(new_message)

    return new_message
