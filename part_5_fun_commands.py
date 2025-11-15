# ==============================
# part_5_fun_commands.py
# أوامر التسلية (م4) - عربي
# ==============================

import random
from datetime import datetime

class FunCommands:
    def __init__(self, db, ranks_system):
        self.db = db
        self.ranks = ranks_system
        
        # رتب التسلية
        self.fun_ranks_arabic = {
            'هطف': {'single': 'هطف', 'plural': 'الهطوف'},
            'بثر': {'single': 'بثر', 'plural': 'البثرين'},
            'حمار': {'single': 'حمار', 'plural': 'الحمير'},
            'كلب': {'single': 'كلب', 'plural': 'الكلاب'},
            'كلبه': {'single': 'كلبه', 'plural': 'الكلبات'},
            'عتوي': {'single': 'عتوي', 'plural': 'العتوين'},
            'عتويه': {'single': 'عتويه', 'plural': 'العتويات'},
            'لحجي': {'single': 'لحجي', 'plural': 'اللحوج'},
            'لحجيه': {'single': 'لحجيه', 'plural': 'اللحجيات'},
            'خروف': {'single': 'خروف', 'plural': 'الخرفان'},
            'خفيفه': {'single': 'خفيفه', 'plural': 'الخفيفات'},
            'خفيف': {'single': 'خفيف', 'plural': 'الخفيفين'}
        }
    
    async def show_fun_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض قائمة التسلية (م4)"""
        help_text = """
🎮 <b>قائمة أوامر التسلية - م4</b>
━━━━━━━━━━━━━━━━━━

<b>👥 رفع رتب ترفيهية:</b>
• رفع هطف
• رفع بثر
• رفع حمار
• رفع كلب
• رفع كلبه
• رفع عتوي
• رفع عتويه
• رفع لحجي
• رفع لحجيه
• رفع خروف
• رفع خفيف
• رفع خفيفه
• رفع بقلبي

• تنزيل هطف
• تنزيل بثر
• إلخ...

<b>💑 أوامر الزواج:</b>
• زواج
• طلاق
• زوجي
• زوجتي
• تتزوجني

<b>📊 أوامر التصويت:</b>
• اكتموه
• تعطيل اكتموه
• تفعيل اكتموه

<b>🛠️ إدارة التسلية:</b>
• مسح رتب التسليه
• رتب التسليه
• تعطيل التسليه
        """
        
        keyboard = [
            [InlineKeyboardButton("🔄 رجوع", callback_data="main_menu")],
            [InlineKeyboardButton("💑 أوامر الزواج", callback_data="marriage_commands")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(help_text, reply_markup=reply_markup, parse_mode='HTML')
    
    async def add_fun_rank(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """رفع رتبة ترفيهية"""
        chat_id = update.effective_chat.id
        
        if not context.args:
            await update.message.reply_text("❌ الاستخدام: رفع <نوع الرتبة> بالرد على الشخص")
            return
        
        rank_type = context.args[0].lower()
        
        if rank_type not in self.fun_ranks_arabic:
            await update.message.reply_text(f"❌ الرتبة غير موجودة\nالرتب المتاحة: {', '.join(self.fun_ranks_arabic.keys())}")
            return
        
        if not update.message.reply_to_message:
            await update.message.reply_text("❌ يجب الرد على الشخص المراد رفعه")
            return
        
        target_user = update.message.reply_to_message.from_user
        assigned_by = update.effective_user.id
        
        # حفظ في قاعدة البيانات
        cursor = self.db.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO fun_ranks 
            (user_id, chat_id, rank_type, assigned_by) 
            VALUES (?, ?, ?, ?)
        ''', (target_user.id, chat_id, rank_type, assigned_by))
        self.db.conn.commit()
        
        rank_info = self.fun_ranks_arabic[rank_type]
        await update.message.reply_text(f"✅ تم رفع {target_user.first_name} إلى {rank_info['single']} بنجاح! 🎉")
    
    async def remove_fun_rank(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """تنزيل رتبة ترفيهية"""
        chat_id = update.effective_chat.id
        
        if not context.args:
            await update.message.reply_text("❌ الاستخدام: تنزيل <نوع الرتبة> بالرد على الشخص")
            return
        
        rank_type = context.args[0].lower()
        
        if not update.message.reply_to_message:
            await update.message.reply_text("❌ يجب الرد على الشخص المراد تنزيله")
            return
        
        target_user = update.message.reply_to_message.from_user
        
        # حذف من قاعدة البيانات
        cursor = self.db.conn.cursor()
        cursor.execute('''
            DELETE FROM fun_ranks 
            WHERE user_id = ? AND chat_id = ? AND rank_type = ?
        ''', (target_user.id, chat_id, rank_type))
        self.db.conn.commit()
        
        if cursor.rowcount > 0:
            rank_info = self.fun_ranks_arabic.get(rank_type, {'single': rank_type})
            await update.message.reply_text(f"✅ تم تنزيل {target_user.first_name} من {rank_info['single']} بنجاح")
        else:
            await update.message.reply_text("❌ المستخدم لا يملك هذه الرتبة")
    
    async def show_fun_ranks(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض رتب التسلية في المجموعة"""
        chat_id = update.effective_chat.id
        
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT user_id, rank_type FROM fun_ranks 
            WHERE chat_id = ?
        ''', (chat_id,))
        
        ranks_data = cursor.fetchall()
        
        if not ranks_data:
            await update.message.reply_text("📭 لا توجد رتب ترفيهية في هذه المجموعة")
            return
        
        # تجميع البيانات
        ranks_dict = {}
        for user_id, rank_type in ranks_data:
            if rank_type not in ranks_dict:
                ranks_dict[rank_type] = []
            ranks_dict[rank_type].append(user_id)
        
        # بناء الرسالة
        message = "🎭 <b>رتب التسلية في المجموعة:</b>\n━━━━━━━━━━━━━━━━━━\n"
        
        for rank_type, users in ranks_dict.items():
            rank_info = self.fun_ranks_arabic.get(rank_type, {'plural': rank_type})
            message += f"\n<b>{rank_info['plural']}:</b> {len(users)} عضو\n"
        
        await update.message.reply_text(message, parse_mode='HTML')
    
    async def marry_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر الزواج"""
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        
        if not update.message.reply_to_message:
            await update.message.reply_text("❌ يجب الرد على الشخص الذي تريد الزواج منه")
            return
        
        target_user = update.message.reply_to_message.from_user
        
        if target_user.id == user_id:
            await update.message.reply_text("❌ لا يمكنك الزواج من نفسك!")
            return
        
        # التحقق إذا كان متزوج بالفعل
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT * FROM marriages 
            WHERE chat_id = ? AND ((user1_id = ? OR user2_id = ?) OR (user1_id = ? OR user2_id = ?)) 
            AND status = 'married'
        ''', (chat_id, user_id, user_id, target_user.id, target_user.id))
        
        existing_marriage = cursor.fetchone()
        
        if existing_marriage:
            await update.message.reply_text("❌ أحدكما متزوج بالفعل!")
            return
        
        # إنشاء الزواج
        cursor.execute('''
            INSERT INTO marriages (user1_id, user2_id, chat_id, status) 
            VALUES (?, ?, ?, ?)
        ''', (user_id, target_user.id, chat_id, 'married'))
        self.db.conn.commit()
        
        await update.message.reply_text(
            f"💍 <b>مبروك للعروسين!</b>\n\n"
            f"👰 {update.effective_user.first_name}\n"
            f"🤵 {target_user.first_name}\n\n"
            f"تم الزواج بنجاح! 💕",
            parse_mode='HTML'
        )
    
    async def divorce_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر الطلاق"""
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        
        # البحث عن الزواج
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT * FROM marriages 
            WHERE chat_id = ? AND (user1_id = ? OR user2_id = ?) AND status = 'married'
        ''', (chat_id, user_id, user_id))
        
        marriage = cursor.fetchone()
        
        if not marriage:
            await update.message.reply_text("❌ لست متزوجاً في هذه المجموعة!")
            return
        
        # تحديث حالة الزواج
        cursor.execute('''
            UPDATE marriages SET status = 'divorced' 
            WHERE chat_id = ? AND (user1_id = ? OR user2_id = ?)
        ''', (chat_id, user_id, user_id))
        self.db.conn.commit()
        
        await update.message.reply_text("💔 تم الطلاق بنجاح... الحياة تستمر!")
    
    async def my_spouse_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض زوجي/زوجتي"""
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT user1_id, user2_id FROM marriages 
            WHERE chat_id = ? AND (user1_id = ? OR user2_id = ?) AND status = 'married'
        ''', (chat_id, user_id, user_id))
        
        marriage = cursor.fetchone()
        
        if not marriage:
            await update.message.reply_text("❌ لست متزوجاً في هذه المجموعة!")
            return
        
        # تحديد الشريك
        spouse_id = marriage[0] if marriage[1] == user_id else marriage[1]
        
        try:
            spouse = await context.bot.get_chat(spouse_id)
            spouse_name = spouse.first_name
            
            await update.message.reply_text(
                f"💑 <b>زوجك/زوجتك:</b>\n"
                f"👤 الاسم: {spouse_name}\n"
                f"🆔 الأيدي: {spouse_id}",
                parse_mode='HTML'
            )
        except:
            await update.message.reply_text("❌ لا يمكن العثور على معلومات الشريك")

# إنشاء كائن أوامر التسلية
fun_commands = FunCommands(db, ranks_system)

print("✅ تم تحميل الجزء 5 بنجاح: أوامر التسلية (م4) - عربي")