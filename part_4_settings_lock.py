# ==============================
# part_4_settings_lock.py
# الإعدادات والقفل (م2 + م3) - عربي
# ==============================

class SettingsAndLockCommands:
    def __init__(self, db, ranks_system):
        self.db = db
        self.ranks = ranks_system
    
    async def show_settings_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض قائمة الإعدادات (م2)"""
        help_text = """
⚙️ <b>قائمة الإعدادات - م2</b>
━━━━━━━━━━━━━━━━━━

<b>👁️ أوامر رؤية الإعدادات:</b>
• الرابط
• المالكين
• المالكين الاساسين
• المنشئين
• الادمنيه
• المدراء
• المميزين
• المحظورين
• القوانين
• المكتومين
• معلوماتي
• الحمايه
• الاعدادات
• المجموعه

<b>🛠️ أوامر وضع الإعدادات:</b>
• اضف رابط
• مسح الرابط
• انشاء رابط
• ضع الترحيب
• ضع قوانين
• ضع رابط
• اضف امر
• تعيين الايدي
• اضف قناه
• حذف قناه

<b>📥 أوامر التحميل:</b>
• تفعيل - تعطيل التحميل
• بحث + اسم الاغنيه
• تيك + الرابط
• ساوند + الرابط
        """
        
        keyboard = [
            [InlineKeyboardButton("🔒 أوامر القفل", callback_data="lock_commands")],
            [InlineKeyboardButton("🔄 رجوع", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(help_text, reply_markup=reply_markup, parse_mode='HTML')
    
    async def show_lock_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض قائمة القفل (م3)"""
        help_text = """
🔒 <b>قائمة القفل والفتح - م3</b>
━━━━━━━━━━━━━━━━━━

<b>أوامر القفل:</b>
• قفل الروابط
• قفل الصور
• قفل الفيديو
• قفل الملصقات
• قفل المتحركه
• قفل الالعاب
• قفل الاغاني
• قفل الجهات
• قفل التاك
• قفل البوتات
• قفل المعرفات
• قفل الكلايش
• قفل التكرار

<b>أوامر الفتح:</b>
• فتح الروابط
• فتح الصور
• فتح الفيديو
• فتح الملصقات
• فتح المتحركه
• فتح الالعاب
• فتح الاغاني
• فتح الجهات
• فتح التاك
• فتح البوتات
• فتح المعرفات
• فتح الكلايش
• فتح التكرار
        """
        
        keyboard = [
            [InlineKeyboardButton("⚙️ الإعدادات", callback_data="settings_commands")],
            [InlineKeyboardButton("🔄 رجوع", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(help_text, reply_markup=reply_markup, parse_mode='HTML')
    
    async def show_group_link(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض رابط المجموعة"""
        chat_id = update.effective_chat.id
        settings = self.db.get_group_settings(chat_id)
        
        if settings.get('group_link'):
            link = settings['group_link']
            await update.message.reply_text(f"🔗 رابط المجموعة:\n{link}")
        else:
            await update.message.reply_text("❌ لم يتم تعيين رابط للمجموعة بعد\n\nاستخدم: اضف رابط <الرابط>")
    
    async def set_group_link(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """تعيين رابط المجموعة"""
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        user_rank = self.db.get_user_rank(user_id, chat_id)
        
        if self.ranks.get_rank_level(user_rank) < 4:  # أقل من منشئ
            await update.message.reply_text("❌ تحتاج رتبة منشئ على الأقل لتعيين الرابط")
            return
        
        if not context.args:
            await update.message.reply_text("❌ الاستخدام: اضف رابط <الرابط>")
            return
        
        link = ' '.join(context.args)
        if not link.startswith(('http://', 'https://', 't.me/')):
            await update.message.reply_text("❌ الرابط غير صالح")
            return
        
        settings = self.db.get_group_settings(chat_id)
        settings['group_link'] = link
        self.db.update_group_settings(chat_id, settings)
        
        await update.message.reply_text("✅ تم حفظ رابط المجموعة بنجاح")
    
    async def create_group_link(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إنشاء رابط للمجموعة"""
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        user_rank = self.db.get_user_rank(user_id, chat_id)
        
        if self.ranks.get_rank_level(user_rank) < 4:  # أقل من منشئ
            await update.message.reply_text("❌ تحتاج رتبة منشئ على الأقل لإنشاء الرابط")
            return
        
        try:
            chat = await context.bot.get_chat(chat_id)
            if chat.invite_link:
                link = chat.invite_link
            else:
                link = await context.bot.create_chat_invite_link(chat_id, creates_join_request=False)
                link = link.invite_link
            
            settings = self.db.get_group_settings(chat_id)
            settings['group_link'] = link
            self.db.update_group_settings(chat_id, settings)
            
            await update.message.reply_text(f"✅ تم إنشاء رابط المجموعة:\n{link}")
            
        except Exception as e:
            await update.message.reply_text("❌ لا يمكنني إنشاء رابط للمجموعة")

# إنشاء كائن الإعدادات والقفل
settings_lock_commands = SettingsAndLockCommands(db, ranks_system)

print("✅ تم تحميل الجزء 4 بنجاح: الإعدادات والقفل (م2 + م3) - عربي")