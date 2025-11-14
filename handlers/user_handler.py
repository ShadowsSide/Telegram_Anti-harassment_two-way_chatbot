from telegram import Update
from telegram.error import BadRequest
from telegram.ext import ContextTypes
from database import models as db
from services.verification import create_verification
from services.thread_manager import get_or_create_thread
from config import config

async def _resend_message(update: Update, context: ContextTypes.DEFAULT_TYPE, thread_id: int):
    message = update.message
    
    
    if message.text:
        await context.bot.send_message(
            chat_id=config.FORUM_GROUP_ID,
            text=message.text,
            entities=message.entities,
            message_thread_id=thread_id,
            disable_web_page_preview=True
        )
    elif message.photo:
        await context.bot.send_photo(
            chat_id=config.FORUM_GROUP_ID,
            photo=message.photo[-1].file_id,
            caption=message.caption,
            caption_entities=message.caption_entities,
            message_thread_id=thread_id
        )
    elif message.animation:
        await context.bot.send_animation(
            chat_id=config.FORUM_GROUP_ID,
            animation=message.animation.file_id,
            caption=message.caption,
            caption_entities=message.caption_entities,
            message_thread_id=thread_id
        )
    elif message.video:
        await context.bot.send_video(
            chat_id=config.FORUM_GROUP_ID,
            video=message.video.file_id,
            caption=message.caption,
            caption_entities=message.caption_entities,
            message_thread_id=thread_id
        )
    elif message.document:
        await context.bot.send_document(
            chat_id=config.FORUM_GROUP_ID,
            document=message.document.file_id,
            caption=message.caption,
            caption_entities=message.caption_entities,
            message_thread_id=thread_id
        )
    elif message.audio:
        await context.bot.send_audio(
            chat_id=config.FORUM_GROUP_ID,
            audio=message.audio.file_id,
            caption=message.caption,
            caption_entities=message.caption_entities,
            message_thread_id=thread_id
        )
    elif message.voice:
        await context.bot.send_voice(
            chat_id=config.FORUM_GROUP_ID,
            voice=message.voice.file_id,
            caption=message.caption,
            caption_entities=message.caption_entities,
            message_thread_id=thread_id
        )
    elif message.video_note:
        await context.bot.send_video_note(
            chat_id=config.FORUM_GROUP_ID,
            video_note=message.video_note.file_id,
            message_thread_id=thread_id
        )
    elif message.sticker:
        await context.bot.send_sticker(
            chat_id=config.FORUM_GROUP_ID,
            sticker=message.sticker.file_id,
            message_thread_id=thread_id
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    
    is_blocked, is_permanent = await db.is_blacklisted(user.id)
    if is_blocked:
        if is_permanent:
            await update.message.reply_text("你已被永久封禁，如有疑问请联系管理员。")
            return
        
        
        from services.blacklist import start_unblock_process
        message, keyboard = await start_unblock_process(user.id)
        if message and keyboard:
            await update.message.reply_text(message, reply_markup=keyboard, parse_mode='Markdown')
        elif message:
            await update.message.reply_text(message)
        return
    
    
    user_data = await db.get_user(user.id)
    if not user_data or not user_data.get('is_verified'):
        
        context.user_data['pending_update'] = update
        question, keyboard = await create_verification(user.id)
        await update.message.reply_text(question, reply_markup=keyboard)
        return
    
    
    thread_id, is_new = await get_or_create_thread(update, context)
    if not thread_id:
        await update.message.reply_text("无法创建或找到您的话题，请联系管理员。")
        return
    
    try:
        
        if not is_new:
            await _resend_message(update, context, thread_id)
    except BadRequest as e:
        if "Message thread not found" in e.message:
            
            await db.update_user_thread_id(user.id, None)
            await db.update_user_verification(user.id, False)
            
            
            context.user_data['pending_update'] = update
            question, keyboard = await create_verification(user.id)
            
            
            full_message = (
                "您的话题已被关闭，请重新进行验证以发送消息。\n\n"
                f"{question}"
            )
            
            await update.message.reply_text(
                text=full_message,
                reply_markup=keyboard
            )
            return
        else:
            print(f"发送消息时发生未知错误: {e}")
            await update.message.reply_text("发送消息时发生未知错误，请稍后再试。")
