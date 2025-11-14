from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from .command_handler import start, help_command, block, unblock, blacklist, stats
from .user_handler import handle_message
from .callback_handler import handle_callback
from .admin_handler import handle_admin_reply
from config import config

def register_handlers(app: Application):
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("block", block))
    app.add_handler(CommandHandler("unblock", unblock))
    app.add_handler(CommandHandler("blacklist", blacklist))
    app.add_handler(CommandHandler("stats", stats))
    
    
    app.add_handler(MessageHandler(
        filters.Chat(chat_id=config.FORUM_GROUP_ID) & filters.REPLY & ~filters.COMMAND,
        handle_admin_reply
    ))
    
    
    app.add_handler(MessageHandler(
        (filters.TEXT | filters.PHOTO | filters.VIDEO | filters.AUDIO | filters.VOICE |
         filters.Document.ALL | filters.Sticker.ALL | filters.ANIMATION) &
        ~filters.COMMAND,
        handle_message
    ))
    
    
    app.add_handler(CallbackQueryHandler(handle_callback))