from telegram import Update
from telegram.ext import ContextTypes
from services.verification import verify_answer
from .user_handler import handle_message

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理内联键盘回调"""
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
        from database import models as db

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
