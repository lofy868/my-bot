# ==============================
# part_7_service_commands.py
# الأوامر الخدمية والأدوات (م6) - عربي
# ==============================

import requests
from urllib.parse import quote

class ServiceCommands:
    def __init__(self, db, ranks_system):
        self.db = db
        self.ranks = ranks_system
    
    async def show_service_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض قائمة الأوامر الخدمية (م6)"""
        help_text = """
🔧 <b>قائمة الأوامر الخدمية - م6</b>
━━━━━━━━━━━━━━━━━━

<b>ℹ️ أوامر المعلومات:</b>
• الايدي - عرض هويتك
• معلوماتي - معلوماتك الكاملة
• الرابط - رابط المجموعة
• القوانين - قوانين المجموعة
• المطور - معلومات المطور

<b>🔍 أوامر البحث:</b>
• بحث + كلمة
• يوتيوب + اسم الفيديو
• انستا + اسم المستخدم
• تيك توك + رابط

<b>🎵 أوامر التحميل:</b>
• ساوند + رابط
• تحميل + رابط

<b>🛠️ أوامر أخرى:</b>
• الالعاب - قائمة الألعاب
• الترحيب - رسالة الترحيب
• السورس - معلومات السورس
        """
        
        keyboard = [
            [InlineKeyboardButton("🔄 رجوع", callback_data="main_menu")],
            [InlineKeyboardButton("🎮 الألعاب", callback_data="games_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(help_text, reply_markup=reply_markup, parse_mode='HTML')
    
    async def show_user_id(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض أيدي المستخدم"""
        user = update.effective_user
        chat_id = update.effective_chat.id
        
        user_rank = self.db.get_user_rank(user.id, chat_id)
        rank_name = self.ranks.get_rank_name_arabic(user_rank)
        
        # الحصول على رتب التسلية
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT rank_type FROM fun_ranks 
            WHERE user_id = ? AND chat_id = ?
        ''', (user.id, chat_id))
        
        fun_ranks = [row[0] for row in cursor.fetchall()]
        fun_ranks_text = "، ".join(fun_ranks) if fun_ranks else "لا يوجد"
        
        id_text = f"""
🆔 <b>معلومات المستخدم</b>
━━━━━━━━━━━━━━━━━━

<b>👤 الاسم:</b> {user.first_name}
<b>🆔 الأيدي:</b> <code>{user.id}</code>
<b>📊 الرتبة:</b> {rank_name}
<b>🎭 رتب التسلية:</b> {fun_ranks_text}

<b>💬 مجموعة:</b> {update.effective_chat.title}
<b>🆔 أيدي المجموعة:</b> <code>{chat_id}</code>
        """
        
        await update.message.reply_text(id_text, parse_mode='HTML')
    
    async def show_my_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض معلوماتي الكاملة"""
        user = update.effective_user
        chat_id = update.effective_chat.id
        
        user_rank = self.db.get_user_rank(user.id, chat_id)
        rank_name = self.ranks.get_rank_name_arabic(user_rank)
        
        # الحصول على معلومات الزواج
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT user1_id, user2_id FROM marriages 
            WHERE chat_id = ? AND (user1_id = ? OR user2_id = ?) AND status = 'married'
        ''', (chat_id, user.id, user.id))
        
        marriage = cursor.fetchone()
        marital_status = "💍 متزوج" if marriage else "💔 أعزب"
        
        # عدد الرتب الترفيهية
        cursor.execute('''
            SELECT COUNT(*) FROM fun_ranks 
            WHERE user_id = ? AND chat_id = ?
        ''', (user.id, chat_id))
        
        fun_ranks_count = cursor.fetchone()[0]
        
        info_text = f"""
📋 <b>معلوماتي الكاملة</b>
━━━━━━━━━━━━━━━━━━

<b>👤 المعلومات الشخصية:</b>
• الاسم: {user.first_name}
• المعرف: @{user.username if user.username else 'لا يوجد'}
• الأيدي: <code>{user.id}</code>
• الحالة: {marital_status}

<b>🎖️ الرتب والصلاحيات:</b>
• الرتبة الأساسية: {rank_name}
• عدد رتب التسلية: {fun_ranks_count}

<b>📊 إحصائيات:</b>
• عضو في المجموعة منذ: الآن
• عدد الرسائل: جاري التطوير
        """
        
        await update.message.reply_text(info_text, parse_mode='HTML')
    
    async def search_youtube(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """بحث في يوتيوب"""
        if not context.args:
            await update.message.reply_text("❌ الاستخدام: يوتيوب <اسم الفيديو>")
            return
        
        search_query = ' '.join(context.args)
        encoded_query = quote(search_query)
        
        youtube_url = f"https://www.youtube.com/results?search_query={encoded_query}"
        
        await update.message.reply_text(
            f"🔍 <b>نتائج البحث على يوتيوب:</b>\n"
            f"الكلمة: {search_query}\n\n"
            f"📺 يمكنك مشاهدة النتائج من هنا:\n"
            f"{youtube_url}",
            parse_mode='HTML',
            disable_web_page_preview=True
        )
    
    async def show_developer_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض معلومات المطور"""
        dev_info = f"""
👑 <b>معلومات المطور</b>
━━━━━━━━━━━━━━━━━━

<b>🆔 الأيدي:</b> <code>{DEVELOPER_ID}</code>
<b>👤 المعرف:</b> {DEVELOPER_USERNAME}
<b>🤖 البوت:</b> {BOT_NAME}

<b>📞 للتواصل:</b>
{DEVELOPER_USERNAME}

<b>📢 قناة البوت:</b>
@lofy_2000

<b>💻 السورس:</b>
تم تطوير البوت بلغة Python
باستخدام مكتبة python-telegram-bot
        """
        
        keyboard = [
            [InlineKeyboardButton("📢 قناة البوت", url="https://t.me/lofy_2000")],
            [InlineKeyboardButton("👤 تواصل مع المطور", url=f"https://t.me/{DEVELOPER_USERNAME[1:]}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(dev_info, reply_markup=reply_markup, parse_mode='HTML')
    
    async def show_group_rules(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض قوانين المجموعة"""
        chat_id = update.effective_chat.id
        settings = self.db.get_group_settings(chat_id)
        
        rules = settings.get('rules_text', '❌ لم يتم تعيين قوانين للمجموعة بعد.\n\nاستخدم: ضع قوانين <النص>')
        
        rules_text = f"""
📜 <b>قوانين المجموعة</b>
━━━━━━━━━━━━━━━━━━

{rules}

⚖️ <b>ملاحظة:</b>
عدم الالتزام بالقوانين يؤدي إلى الحظر.
        """
        
        await update.message.reply_text(rules_text, parse_mode='HTML')
    
    async def download_soundcloud(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """تحميل من ساوند كلاود"""
        if not context.args:
            await update.message.reply_text("❌ الاستخدام: ساوند <رابط ساوندكلاود>")
            return
        
        url = context.args[0]
        
        if 'soundcloud.com' not in url:
            await update.message.reply_text("❌ الرابط يجب أن يكون من ساوندكلاود")
            return
        
        await update.message.reply_text(
            f"🎵 <b>جاري تحميل الملف الصوتي...</b>\n\n"
            f"🔗 الرابط: {url}\n\n"
            f"⏳ قد يستغرق التحميل بضع ثواني",
            parse_mode='HTML'
        )
        
        # هنا يمكن إضافة كود التحميل الفعلي من ساوندكلاود
        # await context.bot.send_audio(chat_id, audio_file)
    
    async def show_games_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض قائمة الألعاب"""
        games_text = """
🎮 <b>قائمة الألعاب المتاحة</b>
━━━━━━━━━━━━━━━━━━

<b>🎯 الألعاب النصية:</b>
• كت vs كت - لعبة XO
• روليت - لعبة الروليت
• تخمين - لعبة تخمين الأرقام
• رياضيات - مسائل رياضية

<b>🎰 ألعاب الحظ:</b>
• زوجني - لعبة الزواج العشوائي
• اكتموه - تصويت لإكمال شخص
• حظ - اختبار حظك

<b>🔮 ألعاب أخرى:</b>
• صلاحيات - لعبة الصلاحيات
• انجليزي - ترجمة كلمات
        """
        
        keyboard = [
            [InlineKeyboardButton("🎯 XO", callback_data="game_xo"), 
             InlineKeyboardButton("🎰 روليت", callback_data="game_roulette")],
            [InlineKeyboardButton("🔮 زوجني", callback_data="game_marry"),
             InlineKeyboardButton("📊 اكتموه", callback_data="game_mute")],
            [InlineKeyboardButton("🔄 رجوع", callback_data="service_commands")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(games_text, reply_markup=reply_markup, parse_mode='HTML')

# إنشاء كائن الأوامر الخدمية
service_commands = ServiceCommands(db, ranks_system)

print("✅ تم تحميل الجزء 7 بنجاح: الأوامر الخدمية (م6) - عربي")