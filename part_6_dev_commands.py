# ==============================
# part_6_dev_commands.py
# أوامر المطور (م5) - عربي
# ==============================

import json
import subprocess
import sys

class DevCommands:
    def __init__(self, db, ranks_system):
        self.db = db
        self.ranks = ranks_system
    
    async def show_dev_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض قائمة المطور (م5)"""
        user_id = update.effective_user.id
        
        if user_id != DEVELOPER_ID:
            await update.message.reply_text("❌ هذا الأمر للمطورين فقط!")
            return
        
        help_text = """
👑 <b>قائمة أوامر المطور - م5</b>
━━━━━━━━━━━━━━━━━━

<b>🛠️ أوامر النظام:</b>
• تحديث - تحديث السورس
• اعاده تشغيل - إعادة تشغيل البوت
• reload - إعادة تحميل

<b>👥 إدارة المطورين:</b>
• رفع Dev
• تنزيل Dev
• مسح المالكين الاساسيين

<b>🌐 الأوامر العامة:</b>
• فتح - قفل ردود MY
• فتح - قفل الاحصائيات
• فتح - قفل حظر العام

<b>⛔ الحظر العام:</b>
• حظر عام
• كتم عام
• الغاء حظر عام
• الغاء كتم عام
• قائمه العام

<b>📝 إدارة الردود:</b>
• اضف رد عام
• اضف رد متعدد عام
• مسح الردود العامه
• الردود العامه

<b>🎮 إدارة الألعاب:</b>
• اضف لعبه عام
• مسح - ضع كليشه الالعاب
• مسح - ضع كليشه م1
• مسح - ضع كليشه م2
• إلخ...
        """
        
        keyboard = [
            [InlineKeyboardButton("🔄 رجوع", callback_data="main_menu")],
            [InlineKeyboardButton("🛠️ أوامر النظام", callback_data="system_commands")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(help_text, reply_markup=reply_markup, parse_mode='HTML')
    
    async def promote_dev(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """رفع مطور ثانوي"""
        user_id = update.effective_user.id
        
        if user_id != DEVELOPER_ID:
            await update.message.reply_text("❌ هذا الأمر للمطور الأساسي فقط!")
            return
        
        if not update.message.reply_to_message:
            await update.message.reply_text("❌ يجب الرد على الشخص المراد رفعه مطور")
            return
        
        target_user = update.message.reply_to_message.from_user
        chat_id = update.effective_chat.id
        
        # رفع المستخدم كمطور في جميع المجموعات
        cursor = self.db.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, chat_id, rank) 
            VALUES (?, ?, ?)
        ''', (target_user.id, 0, 'dev'))  # chat_id = 0 للصلاحيات العامة
        
        self.db.conn.commit()
        
        await update.message.reply_text(f"✅ تم رفع {target_user.first_name} كمطور ثانوي بنجاح")
    
    async def restart_bot(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إعادة تشغيل البوت"""
        user_id = update.effective_user.id
        
        if user_id != DEVELOPER_ID:
            await update.message.reply_text("❌ هذا الأمر للمطور الأساسي فقط!")
            return
        
        await update.message.reply_text("🔄 جاري إعادة تشغيل البوت...")
        
        # إعادة تشغيل البوت
        python = sys.executable
        os.execl(python, python, *sys.argv)
    
    async def broadcast_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """بث رسالة لجميع المجموعات"""
        user_id = update.effective_user.id
        
        if user_id != DEVELOPER_ID:
            await update.message.reply_text("❌ هذا الأمر للمطور الأساسي فقط!")
            return
        
        if not context.args:
            await update.message.reply_text("❌ الاستخدام: ذيع <الرسالة>")
            return
        
        message = ' '.join(context.args)
        
        # الحصول على جميع المجموعات من قاعدة البيانات
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT DISTINCT chat_id FROM users WHERE chat_id > 0')
        groups = cursor.fetchall()
        
        sent_count = 0
        failed_count = 0
        
        await update.message.reply_text(f"📢 جاري البث لـ {len(groups)} مجموعة...")
        
        for group in groups:
            chat_id = group[0]
            try:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"📢 <b>إعلان من المطور:</b>\n\n{message}",
                    parse_mode='HTML'
                )
                sent_count += 1
            except Exception as e:
                failed_count += 1
        
        await update.message.reply_text(
            f"✅ تم الانتهاء من البث:\n"
            f"✅ تم الإرسال: {sent_count}\n"
            f"❌ فشل الإرسال: {failed_count}"
        )
    
    async def bot_statistics(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إحصائيات البوت"""
        user_id = update.effective_user.id
        
        if user_id != DEVELOPER_ID:
            await update.message.reply_text("❌ هذا الأمر للمطور الأساسي فقط!")
            return
        
        cursor = self.db.conn.cursor()
        
        # عدد المجموعات
        cursor.execute('SELECT COUNT(DISTINCT chat_id) FROM users WHERE chat_id > 0')
        groups_count = cursor.fetchone()[0]
        
        # عدد المستخدمين
        cursor.execute('SELECT COUNT(DISTINCT user_id) FROM users')
        users_count = cursor.fetchone()[0]
        
        # عدد الرسائل المحظورة
        cursor.execute('SELECT COUNT(*) FROM restricted_users WHERE restriction_type = "banned"')
        banned_count = cursor.fetchone()[0]
        
        statistics_text = f"""
📊 <b>إحصائيات البوت</b>
━━━━━━━━━━━━━━━━━━

<b>📈 المجموعات:</b> {groups_count}
<b>👥 المستخدمين:</b> {users_count}
<b>🚫 المحظورين:</b> {banned_count}

<b>🤖 معلومات البوت:</b>
• الاسم: {BOT_NAME}
• المطور: {DEVELOPER_USERNAME}
• الإصدار: 2.0
        """
        
        await update.message.reply_text(statistics_text, parse_mode='HTML')
    
    async def add_global_reply(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إضافة رد عام"""
        user_id = update.effective_user.id
        
        if user_id != DEVELOPER_ID:
            await update.message.reply_text("❌ هذا الأمر للمطور الأساسي فقط!")
            return
        
        if len(context.args) < 2:
            await update.message.reply_text("❌ الاستخدام: اضف رد عام <المفتاح> <الرد>")
            return
        
        trigger = context.args[0]
        reply_text = ' '.join(context.args[1:])
        
        cursor = self.db.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO custom_replies 
            (chat_id, trigger, reply_text, reply_type, created_by) 
            VALUES (?, ?, ?, ?, ?)
        ''', (0, trigger, reply_text, 'text', user_id))
        
        self.db.conn.commit()
        
        await update.message.reply_text(f"✅ تم إضافة الرد العام '{trigger}' بنجاح")

# لا ننشئ كائن أوامر المطور هنا - سيتم إنشاؤه في الملف الرئيسي
# dev_commands = DevCommands(db, ranks_system)

print("✅ تم تحميل الجزء 6 بنجاح: أوامر المطور (م5) - عربي")
