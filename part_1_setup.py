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