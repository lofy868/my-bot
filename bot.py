# ==============================
# part_1_setup.py
# الإعدادات الأساسية + قاعدة البيانات
# ==============================

import sqlite3
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
import os
from datetime import datetime

# ====================  الإعدادات الأساسية  ====================
BOT_TOKEN = "8434698011:AAFI4P7_MGQvz8RMm9KjbOXIt-hKoMhThcc"
DEVELOPER_ID = 8092119482
DEVELOPER_USERNAME = "@LOFY_25"
CHANNEL_USERNAME = "@lofy_2000"
BOT_NAME = "لـــوفي"

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ====================  قاعدة البيانات  ====================
class Database:
    def __init__(self):
        self.conn = sqlite3.connect('lofy_bot.db', check_same_thread=False)
        self.create_tables()
    
    def create_tables(self):
        """إنشاء جميع الجداول اللازمة"""
        cursor = self.conn.cursor()
        
        # جدول المستخدمين والرتب
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER,
                chat_id INTEGER,
                rank TEXT DEFAULT 'member',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, chat_id)
            )
        ''')
        
        # جدول الإعدادات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS group_settings (
                chat_id INTEGER PRIMARY KEY,
                welcome_text TEXT,
                rules_text TEXT,
                group_link TEXT,
                welcome_enabled INTEGER DEFAULT 1,
                links_enabled INTEGER DEFAULT 1,
                games_enabled INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول المحظورين والمكتومين
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS restricted_users (
                user_id INTEGER,
                chat_id INTEGER,
                restriction_type TEXT, -- 'banned', 'muted', 'kicked'
                reason TEXT,
                restricted_by INTEGER,
                restricted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, chat_id, restriction_type)
            )
        ''')
        
        # جدول الردود
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS custom_replies (
                chat_id INTEGER,
                trigger TEXT,
                reply_text TEXT,
                reply_type TEXT DEFAULT 'text',
                file_id TEXT,
                created_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (chat_id, trigger)
            )
        ''')
        
        # جدول التسلية والرتب الترفيهية
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fun_ranks (
                user_id INTEGER,
                chat_id INTEGER,
                rank_type TEXT,
                assigned_by INTEGER,
                assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, chat_id, rank_type)
            )
        ''')
        
        # جدول الزواج
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS marriages (
                user1_id INTEGER,
                user2_id INTEGER,
                chat_id INTEGER,
                married_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'married',
                PRIMARY KEY (user1_id, user2_id, chat_id)
            )
        ''')
        
        self.conn.commit()
    
    # ========== دوال المستخدمين والرتب ==========
    def get_user_rank(self, user_id: int, chat_id: int) -> str:
        """الحصول على رتبة المستخدم"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT rank FROM users WHERE user_id = ? AND chat_id = ?', (user_id, chat_id))
        result = cursor.fetchone()
        return result[0] if result else 'member'
    
    def set_user_rank(self, user_id: int, chat_id: int, rank: str):
        """تعيين رتبة للمستخدم"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, chat_id, rank) 
            VALUES (?, ?, ?)
        ''', (user_id, chat_id, rank))
        self.conn.commit()
    
    def remove_user_rank(self, user_id: int, chat_id: int):
        """إزالة جميع رتب المستخدم"""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM users WHERE user_id = ? AND chat_id = ?', (user_id, chat_id))
        self.conn.commit()
    
    # ========== دوال الإعدادات ==========
    def get_group_settings(self, chat_id: int) -> dict:
        """الحصول على إعدادات المجموعة"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM group_settings WHERE chat_id = ?', (chat_id,))
        result = cursor.fetchone()
        if result:
            return {
                'chat_id': result[0],
                'welcome_text': result[1],
                'rules_text': result[2],
                'group_link': result[3],
                'welcome_enabled': bool(result[4]),
                'links_enabled': bool(result[5]),
                'games_enabled': bool(result[6])
            }
        return {}
    
    def update_group_settings(self, chat_id: int, settings: dict):
        """تحديث إعدادات المجموعة"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO group_settings 
            (chat_id, welcome_text, rules_text, group_link, welcome_enabled, links_enabled, games_enabled)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            chat_id,
            settings.get('welcome_text'),
            settings.get('rules_text'),
            settings.get('group_link'),
            int(settings.get('welcome_enabled', 1)),
            int(settings.get('links_enabled', 1)),
            int(settings.get('games_enabled', 1))
        ))
        self.conn.commit()

# إنشاء كائن قاعدة البيانات
db = Database()

print("✅ تم تحميل الجزء 1 بنجاح: الإعدادات الأساسية + قاعدة البيانات")
# ==============================
# part_2_ranks_system.py
# نظام الرتب والصلاحيات - عربي
# ==============================

class RanksSystem:
    def __init__(self, database):
        self.db = database
        self.ranks_hierarchy = {
            'member': 0,      # عضو عادي
            'vip': 1,         # مميز
            'admin': 2,       # أدمن
            'manager': 3,     # مدير
            'creator': 4,     # منشئ
            'owner': 5,       # مالك
            'main_owner': 6,  # مالك أساسي
            'dev': 7          # مطور
        }
    
    def get_rank_level(self, rank: str) -> int:
        """الحصول على مستوى الرتبة"""
        return self.ranks_hierarchy.get(rank, 0)
    
    def can_promote(self, promoter_rank: str, target_rank: str) -> bool:
        """التحقق إذا كان يمكن الترقية"""
        promoter_level = self.get_rank_level(promoter_rank)
        target_level = self.get_rank_level(target_rank)
        return promoter_level > target_level
    
    def get_rank_name_arabic(self, rank: str) -> str:
        """الحصول على اسم الرتبة بالعربي"""
        rank_names = {
            'member': 'عضو',
            'vip': 'مميز', 
            'admin': 'أدمن',
            'manager': 'مدير',
            'creator': 'منشئ',
            'owner': 'مالك',
            'main_owner': 'مالك أساسي',
            'dev': 'مطور'
        }
        return rank_names.get(rank, 'عضو')
    
    def promote_user(self, promoter_id: int, target_id: int, chat_id: int, target_rank: str) -> str:
        """ترقية مستخدم مع التحقق من الصلاحيات"""
        # منع ترقية النفس
        if promoter_id == target_id:
            return "❌ لا يمكنك ترقية نفسك"
        
        # الحصول على رتبة المروج والهدف
        promoter_rank = self.db.get_user_rank(promoter_id, chat_id)
        current_target_rank = self.db.get_user_rank(target_id, chat_id)
        
        # التحقق من الصلاحيات
        if not self.can_promote(promoter_rank, target_rank):
            return f"❌ لا يمكنك رفع {self.get_rank_name_arabic(target_rank)} - تحتاج رتبة أعلى"
        
        if not self.can_promote(promoter_rank, current_target_rank):
            return f"❌ لا يمكنك تعديل رتبة {self.get_rank_name_arabic(current_target_rank)} - رتبته أعلى منك"
        
        # تنفيذ الترقية
        self.db.set_user_rank(target_id, chat_id, target_rank)
        
        promoter_name = self.get_rank_name_arabic(promoter_rank)
        target_rank_name = self.get_rank_name_arabic(target_rank)
        
        return f"✅ تم رفع المستخدم إلى {target_rank_name} بنجاح\n👤 الرافع: {promoter_name}"
    
    def demote_user(self, demoter_id: int, target_id: int, chat_id: int) -> str:
        """تنزيل مستخدم مع التحقق من الصلاحيات"""
        if demoter_id == target_id:
            return "❌ لا يمكنك تنزيل نفسك"
        
        demoter_rank = self.db.get_user_rank(demoter_id, chat_id)
        target_rank = self.db.get_user_rank(target_id, chat_id)
        
        if not self.can_promote(demoter_rank, target_rank):
            return f"❌ لا يمكنك تنزيل {self.get_rank_name_arabic(target_rank)} - رتبته أعلى منك"
        
        # تنزيل إلى رتبة عضو عادي
        self.db.set_user_rank(target_id, chat_id, 'member')
        
        return f"✅ تم تنزيل المستخدم إلى عضو عادي بنجاح"
    
    def remove_all_ranks(self, remover_id: int, target_id: int, chat_id: int) -> str:
        """إزالة جميع الرتب من مستخدم"""
        if remover_id == target_id:
            return "❌ لا يمكنك إزالة رتب نفسك"
        
        remover_rank = self.db.get_user_rank(remover_id, chat_id)
        target_rank = self.db.get_user_rank(target_id, chat_id)
        
        if not self.can_promote(remover_rank, target_rank):
            return f"❌ لا يمكنك إزالة رتب {self.get_rank_name_arabic(target_rank)} - رتبته أعلى منك"
        
        self.db.remove_user_rank(target_id, chat_id)
        return "✅ تم إزالة جميع الرتب من المستخدم بنجاح"

# إنشاء كائن نظام الرتب
ranks_system = RanksSystem(db)

print("✅ تم تحميل الجزء 2 بنجاح: نظام الرتب والصلاحيات - عربي")
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
• رفع مالك اساسي
• رفع مالك
• رفع مشرف
• رفع منشئ
• رفع مدير
• رفع ادمن
• رفع مميز

• تنزيل مالك اساسي
• تنزيل مالك
• تنزيل مشرف
• تنزيل منشئ
• تنزيل مدير
• تنزيل ادمن
• تنزيل مميز
• تنزيل الكل

<b>🗑️ أوامر المسح:</b>
• مسح الكل
• مسح المنشئين
• مسح المدراء
• مسح المالكين
• مسح الادمنيه
• مسح المميزين
• مسح المحظورين
• مسح المكتومين
• مسح + عدد
• مسح بالرد

<b>🚫 أوامر الطرد والحظر:</b>
• حظر
• طرد
• كتم
• تقييد
• الغاء حظر
• الغاء كتم
• فك تقييد
• طرد البوتات
• طرد المحذوفين
• كشف البوتات
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

# إنشاء كائن أوامر المطور
dev_commands = DevCommands(db, ranks_system)

print("✅ تم تحميل الجزء 6 بنجاح: أوامر المطور (م5) - عربي")
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
# ==============================
# part_8_main_bot.py
# الملف الرئيسي والتشغيل - عربي
# ==============================

from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
import asyncio

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
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر البدء /start"""
        user = update.effective_user
        chat_id = update.effective_chat.id
        
        welcome_text = f"""
🎊 <b>أهلاً وسهلاً بك {user.first_name}!</b>

🤖 <b>أنا بوت</b> {BOT_NAME}
👑 <b>مطور السورس:</b> {DEVELOPER_USERNAME}

📚 <b>الأوامر المتاحة:</b>
• م1 - أوامر الإدارة
• م2 - أوامر الإعدادات  
• م3 - أوامر القفل والفتح
• م4 - أوامر التسلية
• م5 - أوامر المطور
• م6 - الأوامر الخدمية

🔗 <b>قناة البوت:</b> @lofy_2000
        """
        
        keyboard = [
            [InlineKeyboardButton("📚 الأوامر", callback_data="main_menu")],
            [InlineKeyboardButton("👤 المطور", url=f"https://t.me/{DEVELOPER_USERNAME[1:]}")],
            [InlineKeyboardButton("📢 قناتنا", url="https://t.me/lofy_2000")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='HTML')
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    
    async def handle_messages(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    
    def run_bot(self):
        """تشغيل البوت"""
        print(f"🚀 بدء تشغيل بوت {BOT_NAME}...")
        print(f"👤 المطور: {DEVELOPER_USERNAME}")
        print(f"🆔 أيدي المطور: {DEVELOPER_ID}")
        
        # إنشاء تطبيق البوت
        self.application = Application.builder().token(BOT_TOKEN).build()
        
        # إعداد ال handlers
        self.setup_handlers()
        
        # بدء البوت
        print("✅ البوت يعمل الآن...")
        self.application.run_polling()

# ==================== التشغيل الرئيسي ====================
if __name__ == "__main__":
    bot = LofyBot()
    bot.run_bot()
