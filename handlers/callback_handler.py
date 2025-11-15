from telegram import Update
from telegram.ext import ContextTypes
from services.verification import verify_answer
from services.gemini_service import gemini_service
from database import models as db
from utils.media_converter import sticker_to_image
from .user_handler import handle_message

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = query.from_user.id
    
    if data.startswith("verify_"):
        answer = data.split("_", 1)[1]
        success, message, is_banned = await verify_answer(user_id, answer)
        
        if is_banned:
            await query.edit_message_text(text=message, reply_markup=None)
            return
        
        await query.edit_message_text(text=message)

        if success:
            if 'pending_update' in context.user_data:
                pending_update = context.user_data.pop('pending_update')
                message = pending_update.message
                image_bytes = None

                if message.photo:
                    photo_file = await message.photo[-1].get_file()
                    image_bytes = await photo_file.download_as_bytearray()
                elif message.sticker and not message.sticker.is_animated and not message.sticker.is_video:
                    sticker_file = await message.sticker.get_file()
                    sticker_bytes = await sticker_file.download_as_bytearray()
                    image_bytes = await sticker_to_image(sticker_bytes)

                should_forward = True
                if message.video or message.animation:
                    pass
                else:
                    analyzing_message = await context.bot.send_message(
                        chat_id=message.chat_id,
                        text="正在通过AI分析内容是否包含垃圾信息...",
                        reply_to_message_id=message.message_id
                    )
                    analysis_result = await gemini_service.analyze_message(message, image_bytes)
                    if analysis_result.get("is_spam"):
                        should_forward = False
                        media_type = None
                        media_file_id = None
                        if message.photo:
                            media_type = "photo"
                            media_file_id = message.photo[-1].file_id
                        elif message.sticker:
                            media_type = "sticker"
                            media_file_id = message.sticker.file_id

                        await db.save_filtered_message(
                            user_id=user_id,
                            message_id=message.message_id,
                            content=message.text or message.caption,
                            reason=analysis_result.get("reason"),
                            media_type=media_type,
                            media_file_id=media_file_id,
                        )
                        reason = analysis_result.get("reason", "未提供原因")
                        await analyzing_message.edit_text(f"您的消息已被系统拦截，因此未被转发\n\n原因：{reason}")
                    else:
                        await analyzing_message.delete()

                if should_forward:
                    await handle_message(pending_update, context)
            else:
                await query.message.reply_text("现在您可以发送消息了！")
    
    elif data.startswith("unblock_"):
        from services.blacklist import verify_unblock_answer
        answer = data.split("_", 1)[1]
        message, success = await verify_unblock_answer(user_id, answer)
        
        await query.edit_message_text(text=message, reply_markup=None)
        
    elif data.startswith("admin_unblock_"):
        from services import blacklist
        
        user_id_to_unblock = int(data.split("_")[2])
        
        if not await db.is_admin(user_id):
            await query.answer("抱歉，您没有权限执行此操作。", show_alert=True)
            return
            
        response = await blacklist.unblock_user(user_id_to_unblock)
        await query.answer(response, show_alert=True)
        
        message, keyboard = await blacklist.get_blacklist_keyboard()
        if keyboard:
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text(text=message)
