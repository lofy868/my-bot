# ==============================
# part_8_main_bot.py
# الملف الرئيسي والتشغيل - عربي بالكامل
# ==============================

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
import asyncio
from flask import Flask, request
import os

# استيراد جميع الأجزاء الأخرى
from part_1_setup import db, BOT_TOKEN, DEVELOPER_ID, DEVELOPER_USERNAME, CHANNEL_USERNAME, BOT_NAME
from part_2_ranks_system import ranks_system
from part_3_admin_commands import admin_commands
from part_4_settings_lock import settings_lock_commands
from part_5_fun_commands import fun_commands
from part_6_dev_commands import dev_commands
from part_7_service_commands import service_commands

# إنشاء تطبيق Flask لخادم الويب
app = Flask(__name__)

class LofyBot:
    def __init__(self):
        self.application = None
        self.db = db
        self.ranks_system = ranks_system
    
    def setup_handlers(self):
        """إعداد جميع handlers للأوامر"""
        
        # ==================== الأوامر الرئيسية ====================
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("م1", admin_commands.show_admin_help))
        self.application.add_handler(CommandHandler("م2", settings_lock_commands.show_settings_help))
        self.application.add_handler(CommandHandler("م3", settings_lock_commands.show_lock_help))
        self.application.add_handler(CommandHandler("م4", fun_commands.show_fun_help))
        self.application.add_handler(CommandHandler("م5", dev_commands.show_dev_help))
        self.application.add_handler(CommandHandler("م6", service_commands.show_service_help))
        
        # ==================== أوامر الإدارة (م1) ====================
        self.application.add_handler(CommandHandler("رفع", admin_commands.promote_command))
        self.application.add_handler(CommandHandler("تنزيل", admin_commands.demote_command))
        self.application.add_handler(CommandHandler("تنزيل_الكل", admin_commands.remove_all_ranks_command))
        self.application.add_handler(CommandHandler("مسح", admin_commands.clean_command))
        self.application.add_handler(CommandHandler("حظر", admin_commands.ban_command))
        
        # ==================== أوامر الإعدادات (م2) ====================
        self.application.add_handler(CommandHandler("رابط", settings_lock_commands.show_group_link))
        self.application.add_handler(CommandHandler("اضف_رابط", settings_lock_commands.set_group_link))
        self.application.add_handler(CommandHandler("انشاء_رابط", settings_lock_commands.create_group_link))
        
        # ==================== أوامر التسلية (م4) ====================
        self.application.add_handler(CommandHandler("زواج", fun_commands.marry_command))
        self.application.add_handler(CommandHandler("طلاق", fun_commands.divorce_command))
        self.application.add_handler(CommandHandler("زوجي", fun_commands.my_spouse_command))
        self.application.add_handler(CommandHandler("زوجتي", fun_commands.my_spouse_command))
        
        # أوامر رفع رتب التسلية
        for rank_name in fun_commands.fun_ranks_arabic.keys():
            self.application.add_handler(CommandHandler(f"رفع_{rank_name}", fun_commands.add_fun_rank))
            self.application.add_handler(CommandHandler(f"تنزيل_{rank_name}", fun_commands.remove_fun_rank))
        
        self.application.add_handler(CommandHandler("رتب_التسليه", fun_commands.show_fun_ranks))
        
        # ==================== أوامر المطور (م5) ====================
        self.application.add_handler(CommandHandler("تحديث", dev_commands.restart_bot))
        self.application.add_handler(CommandHandler("اعاده_تشغيل", dev_commands.restart_bot))
        self.application.add_handler(CommandHandler("reload", dev_commands.restart_bot))
        self.application.add_handler(CommandHandler("رفع_Dev", dev_commands.promote_dev))
        self.application.add_handler(CommandHandler("ذيع", dev_commands.broadcast_message))
        self.application.add_handler(CommandHandler("الاحصائيات", dev_commands.bot_statistics))
        self.application.add_handler(CommandHandler("اضف_رد_عام", dev_commands.add_global_reply))
        
        # ==================== الأوامر الخدمية (م6) ====================
        self.application.add_handler(CommandHandler("الايدي", service_commands.show_user_id))
        self.application.add_handler(CommandHandler("معلوماتي", service_commands.show_my_info))
        self.application.add_handler(CommandHandler("المطور", service_commands.show_developer_info))
        self.application.add_handler(CommandHandler("القوانين", service_commands.show_group_rules))
        self.application.add_handler(CommandHandler("يوتيوب", service_commands.search_youtube))
        self.application.add_handler(CommandHandler("ساوند", service_commands.download_soundcloud))
        self.application.add_handler(CommandHandler("الالعاب", service_commands.show_games_menu))
        
        # ==================== handlers للردود ====================
        self.application.add_handler(CallbackQueryHandler(self.button_handler))
        
        # handler للرسائل العامة
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_messages))
    
    async def start_command(self, update: Update, context: CallbackContext):
        """أمر البدء /start"""
        user = update.effective_user
        chat_id = update.effective_chat.id
        
        welcome_text = f"""
🎊 <b>أهلاً وسهلاً بك {user.first_name}!</b>

🤖 <b>أنا بوت</b> {BOT_NAME}
👑 <b>مطور السورس:</b> {DEVELOPER_USERNAME}

📚 <b>الأوامر المتاحة:</b>
• م1 : اوامر الادمنيه
• م2 : اوامر الاعدادات
• م3 : اوامر القفل - الفتح
• م4 : اوامر التسليه
• م5 : اوامر Dev
• م6 : الاوامر الخدميه 
━━━━━━━━━━━━━━━━━━

🔗 <b>قناة البوت:</b> @lofy_2000
        """
        
        keyboard = [
            [InlineKeyboardButton("📚 الأوامر", callback_data="main_menu")],
            [InlineKeyboardButton("👤 المطور", url=f"https://t.me/{DEVELOPER_USERNAME[1:]}")],
            [InlineKeyboardButton("📢 قناتنا", url="https://t.me/lofy_2000")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='HTML')
    
    async def button_handler(self, update: Update, context: CallbackContext):
        """معالجة ضغطات الأزرار"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data == "main_menu":
            await self.show_main_menu(query)
        elif data == "clean_commands":
            await admin_commands.show_admin_help(update, context)
        elif data == "games_menu":
            await service_commands.show_games_menu(update, context)
        elif data.startswith("game_"):
            await self.handle_game_query(query, data)
    
    async def show_main_menu(self, query):
        """عرض القائمة الرئيسية"""
        menu_text = """
🎯 <b>القائمة الرئيسية</b>
━━━━━━━━━━━━━━━━━━

◂ م1 : اوامر الادمنيه
◂ م2 : اوامر الاعدادات  
◂ م3 : اوامر القفل - الفتح
◂ م4 : اوامر التسليه
◂ م5 : اوامر Dev
◂ م6 : الاوامر الخدميه 
━━━━━━━━━━━━━━━━━━
        """
        
        keyboard = [
            [InlineKeyboardButton("👑 م1 - الإدارة", callback_data="admin_commands"),
             InlineKeyboardButton("⚙️ م2 - الإعدادات", callback_data="settings_commands")],
            [InlineKeyboardButton("🔒 م3 - القفل", callback_data="lock_commands"),
             InlineKeyboardButton("🎮 م4 - التسلية", callback_data="fun_commands")],
            [InlineKeyboardButton("👑 م5 - المطور", callback_data="dev_commands"),
             InlineKeyboardButton("🔧 م6 - الخدمية", callback_data="service_commands")],
            [InlineKeyboardButton("❌ إغلاق", callback_data="close_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(menu_text, reply_markup=reply_markup, parse_mode='HTML')
    
    async def handle_game_query(self, query, game_type):
        """معالجة ألعاب الأزرار"""
        games_responses = {
            "game_xo": "🎯 لعبة XO قريباً...",
            "game_roulette": "🎰 لعبة الروليت قريباً...", 
            "game_marry": "🔮 لعبة زوجني قريباً...",
            "game_mute": "📊 لعبة اكتموه قريباً..."
        }
        
        response = games_responses.get(game_type, "⚙️ هذه اللعبة قيد التطوير")
        await query.edit_message_text(response)
    
    async def handle_messages(self, update: Update, context: CallbackContext):
        """معالجة الرسائل العادية"""
        message_text = update.message.text
        chat_id = update.effective_chat.id
        
        # التحقق من الردود المخصصة
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT reply_text, reply_type FROM custom_replies 
            WHERE chat_id IN (0, ?) AND trigger = ?
            ORDER BY chat_id DESC LIMIT 1
        ''', (chat_id, message_text.lower()))
        
        reply = cursor.fetchone()
        
        if reply:
            reply_text, reply_type = reply
            await update.message.reply_text(reply_text)

# إنشاء كائن البوت
bot = LofyBot()

# routes لـ Flask
@app.route('/')
def home():
    return f"""
    <html>
        <head>
            <title>{BOT_NAME} Bot</title>
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                .arabic {{ direction: rtl; }}
            </style>
        </head>
        <body>
            <div class="arabic">
                <h1>🤖 بوت {BOT_NAME}</h1>
                <p>البوت يعمل بنجاح على Render! 🎉</p>
                <p>👤 المطور: {DEVELOPER_USERNAME}</p>
                <p>🔗 قناة البوت: {CHANNEL_USERNAME}</p>
            </div>
        </body>
    </html>
    """

@app.route('/webhook', methods=['POST'])
def webhook():
    """معالجة webhook من Telegram"""
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = Update.de_json(json_string, bot.application.bot)
        bot.application.process_update(update)
        return 'OK'
    return 'ERROR'

@app.route('/health')
def health_check():
    """فحص صحة التطبيق"""
    return {'status': 'healthy', 'bot': BOT_NAME, 'developer': DEVELOPER_USERNAME}

# التشغيل الرئيسي
if __name__ == "__main__":
    # إنشاء تطبيق البوت
    bot.application = Application.builder().token(BOT_TOKEN).build()
    bot.setup_handlers()
    
    # الحصول على البورت من Render
    port = int(os.environ.get('PORT', 5000))
    
    print(f"🚀 بدء تشغيل بوت {BOT_NAME} على المنفذ {port}...")
    print(f"👤 المطور: {DEVELOPER_USERNAME}")
    print(f"🆔 أيدي المطور: {DEVELOPER_ID}")
    
    # استخدام webhook إذا كان على Render
    render_url = os.environ.get('RENDER_EXTERNAL_URL')
    if render_url:
        # تشغيل على Render باستخدام webhook
        webhook_url = f"{render_url}/webhook"
        bot.application.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path="webhook",
            webhook_url=webhook_url
        )
        print(f"✅ تم تعيين webhook: {webhook_url}")
    else:
        # تشغيل محلي باستخدام polling
        print("🔍 التشغيل المحلي باستخدام polling...")
        bot.application.run_polling()
