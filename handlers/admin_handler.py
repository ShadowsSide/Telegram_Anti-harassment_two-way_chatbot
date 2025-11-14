from telegram import Update
from telegram.ext import ContextTypes
from database import models as db

async def _send_reply_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    message = update.message
    
    
    if message.text:
        await context.bot.send_message(
            chat_id=user_id,
            text=message.text,
            entities=message.entities,
            disable_web_page_preview=True
        )
    elif message.photo:
        await context.bot.send_photo(
            chat_id=user_id,
            photo=message.photo[-1].file_id,
            caption=message.caption,
            caption_entities=message.caption_entities
        )
    elif message.animation:
        await context.bot.send_animation(
            chat_id=user_id,
            animation=message.animation.file_id,
            caption=message.caption,
            caption_entities=message.caption_entities
        )
    elif message.video:
        await context.bot.send_video(
            chat_id=user_id,
            video=message.video.file_id,
            caption=message.caption,
            caption_entities=message.caption_entities
        )
    elif message.document:
        await context.bot.send_document(
            chat_id=user_id,
            document=message.document.file_id,
            caption=message.caption,
            caption_entities=message.caption_entities
        )
    elif message.audio:
        await context.bot.send_audio(
            chat_id=user_id,
            audio=message.audio.file_id,
            caption=message.caption,
            caption_entities=message.caption_entities
        )
    elif message.voice:
        await context.bot.send_voice(
            chat_id=user_id,
            voice=message.voice.file_id,
            caption=message.caption,
            caption_entities=message.caption_entities
        )
    elif message.video_note:
        await context.bot.send_video_note(
            chat_id=user_id,
            video_note=message.video_note.file_id
        )
    elif message.sticker:
        await context.bot.send_sticker(
            chat_id=user_id,
            sticker=message.sticker.file_id
        )

async def handle_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.is_topic_message:
        return
    
    thread_id = update.message.message_thread_id
    
    
    user = await db.get_user_by_thread_id(thread_id)
    if not user:
        return
    
    user_id = user['user_id']
    
    await _send_reply_to_user(update, context, user_id)