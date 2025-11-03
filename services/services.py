from sqlalchemy.future import select
import uuid

from models.chat import ChatThread, ChatMessage
import uuid

async def create_thread(user_id, message, db):
    new_thread = ChatThread(user_id=user_id, title=message[:20] + "...")
    db.add(new_thread)
    await db.commit()
    await db.refresh(new_thread)

    return new_thread.id

async def add_message_to_thread(thread_id, user_id, message, sender_role, db):
    new_message = ChatMessage(
        thread_id=thread_id,
        user_id=user_id,
        message=message,
        sender_role=sender_role
    )
    db.add(new_message)
    await db.commit()
    await db.refresh(new_message)

    return new_message.id

async def get_thread_messages(thread_id, db):
    result = await db.execute(
        select(ChatMessage).where(ChatMessage.thread_id == thread_id).order_by(ChatMessage.created_at)
    )
    messages = result.scalars().all()
    return messages