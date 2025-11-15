# ==============================
# part_3_admin_commands.py
# أوامر الإدارة (م1) - عربي
# ==============================

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import html

class AdminCommands:
    def __init__(self, db, ranks_system):
        self.db = db
        self.ranks = ranks_system
    
    async def show_admin_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض قائمة أوامر الإدارة (م1)"""
        help_text = """
🎯 <b>قائمة أوامر الإدارة - م1</b>
━━━━━━━━━━━━━━━━━━

<b>👑 أوامر الرفع والتنزيل:</b>
• رفع - تنزيل مالك اساسي
• رفع - تنزيل مالك
• رفع - تنزيل مشرف
• رفع - تنزيل منشئ
• رفع - تنزيل مدير
• رفع - تنزيل ادمن
• رفع - تنزيل مميز
• تنزيل الكل - لازاله جميع الرتب اعلاه

<b>🗑️ أوامر المسح:</b>
• مسح الكل 
• مسح المنشئين
• مسح المدراء
• مسح المالكين
• مسح الادمنيه
• مسح المميزين
• مسح المحظورين
• مسح المكتومين
• مسح قائمه المنع
• مسح الردود
•مسح الاوامر المضافه
• مسح + عدد
• مسح بالرد
• مسح الايدي
• مسح الترحيب
• مسح الرابط


<b>🚫 أوامر الطرد والحظر:</b>
• تقييد + الوقت
• حظر 
• طرد 
• كتم
• تقييد 
• الغاء الحظر 
• الغاء الكتم
• فك التقييد 
• رفع القيود
• منع بالرد
• الغاء منع بالرد
• طرد البوتات
• طرد المحذوفين
• كشف البوتات
━━━━━━━━━━━━━━━━━━
        """
        
        keyboard = [
            [InlineKeyboardButton("🔄 رجوع", callback_data="main_menu")],
            [InlineKeyboardButton("🗑️ أوامر المسح", callback_data="clean_commands")],
            [InlineKeyboardButton("🚫 أوامر الحظر", callback_data="ban_commands")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(help_text, reply_markup=reply_markup, parse_mode='HTML')
    
    async def promote_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر رفع رتبة"""
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        
        if not context.args:
            await update.message.reply_text("❌ الاستخدام: رفع <username/رد> <الرتبة>")
            return
        
        # التعامل مع الردود
        if update.message.reply_to_message:
            target_user = update.message.reply_to_message.from_user
            rank_name = context.args[0].lower()
        else:
            if len(context.args) < 2:
                await update.message.reply_text("❌ الاستخدام: رفع <username/رد> <الرتبة>")
                return
            # هنا يمكن إضافة جلب المستخدم من اليوزرنيم
            target_user = update.message.from_user  # مؤقت
            rank_name = context.args[1].lower()
        
        rank_mapping = {
            'مميز': 'vip',
            'ادمن': 'admin',
            'مدير': 'manager',
            'منشئ': 'creator',
            'مالك': 'owner',
            'مالك_اساسي': 'main_owner',
            'مشرف': 'admin'
        }
        
        target_rank = rank_mapping.get(rank_name)
        if not target_rank:
            await update.message.reply_text("❌ الرتبة غير صحيحة: (مميز، ادمن، مدير، منشئ، مالك، مالك_اساسي)")
            return
        
        result = self.ranks.promote_user(user_id, target_user.id, chat_id, target_rank)
        await update.message.reply_text(result)
    
    async def demote_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر تنزيل رتبة"""
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        
        if update.message.reply_to_message:
            target_user = update.message.reply_to_message.from_user
        else:
            await update.message.reply_text("❌ يجب الرد على الشخص المراد تنزيله")
            return
        
        result = self.ranks.demote_user(user_id, target_user.id, chat_id)
        await update.message.reply_text(result)
    
    async def remove_all_ranks_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر تنزيل الكل"""
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        
        if update.message.reply_to_message:
            target_user = update.message.reply_to_message.from_user
        else:
            await update.message.reply_text("❌ يجب الرد على الشخص المراد تنزيل جميع رتبه")
            return
        
        result = self.ranks.remove_all_ranks(user_id, target_user.id, chat_id)
        await update.message.reply_text(result)
    
    async def clean_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر مسح الرسائل"""
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        user_rank = self.db.get_user_rank(user_id, chat_id)
        
        if self.ranks.get_rank_level(user_rank) < 2:  # أقل من أدمن
            await update.message.reply_text("❌ تحتاج رتبة أدمن على الأقل لاستخدام هذا الأمر")
            return
        
        if not context.args:
            await update.message.reply_text("❌ الاستخدام: مسح <عدد> أو مسح بالرد")
            return
        
        if context.args[0] == "بالرد":
            if not update.message.reply_to_message:
                await update.message.reply_text("❌ يجب الرد على الرسالة المراد مسحها")
                return
            
            try:
                await update.message.reply_to_message.delete()
                await update.message.delete()
                return
            except Exception as e:
                await update.message.reply_text("❌ لا يمكنني مسح هذه الرسالة")
                return
        
        try:
            count = int(context.args[0])
            if count > 100:
                await update.message.reply_text("❌ الحد الأقصى للمسح هو 100 رسالة")
                return
            
            # مسح الرسائل
            messages_deleted = 0
            async for message in context.bot.get_chat_history(chat_id, limit=count + 1):
                try:
                    await message.delete()
                    messages_deleted += 1
                except:
                    continue
                
                if messages_deleted >= count:
                    break
            
            msg = await update.message.reply_text(f"✅ تم مسح {messages_deleted} رسالة")
            
            # مسح رسالة التأكيد بعد 3 ثواني
            await context.bot.delete_message(chat_id, msg.message_id)
            
        except ValueError:
            await update.message.reply_text("❌ يجب إدخال عدد صحيح")
    
    async def ban_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر حظر مستخدم"""
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        user_rank = self.db.get_user_rank(user_id, chat_id)
        
        if self.ranks.get_rank_level(user_rank) < 2:  # أقل من أدمن
            await update.message.reply_text("❌ تحتاج رتبة أدمن على الأقل لاستخدام هذا الأمر")
            return
        
        if not update.message.reply_to_message:
            await update.message.reply_text("❌ يجب الرد على الشخص المراد حظره")
            return
        
        target_user = update.message.reply_to_message.from_user
        
        try:
            # حظر المستخدم
            await context.bot.ban_chat_member(chat_id, target_user.id)
            
            # حفظ في قاعدة البيانات
            cursor = self.db.conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO restricted_users 
                (user_id, chat_id, restriction_type, restricted_by, reason) 
                VALUES (?, ?, ?, ?, ?)
            ''', (target_user.id, chat_id, 'banned', user_id, 'حظر يدوي'))
            self.db.conn.commit()
            
            await update.message.reply_text(f"✅ تم حظر المستخدم {target_user.first_name}")
            
        except Exception as e:
            await update.message.reply_text("❌ لا يمكنني حظر هذا المستخدم")

# إنشاء كائن أوامر الإدارة
admin_commands = AdminCommands(db, ranks_system)

print("✅ تم تحميل الجزء 3 بنجاح: أوامر الإدارة (م1) - عربي")