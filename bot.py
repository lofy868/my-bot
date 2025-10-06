import logging
import random
import sqlite3
import telebot
from datetime import datetime, timedelta
from telebot import types
import re

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# توكن البوت
TOKEN = "8249898760:AAF4ulK4SXF4-sOpyLqQeM_ZnoUr6H6Wrvw"

# إنشاء كائن البوت
bot = telebot.TeleBot(TOKEN)

# قاعدة البيانات
def init_db():
    conn = sqlite3.connect('bot_data.db', check_same_thread=False)
    cursor = conn.cursor()
    
    # جدول الألعاب
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_balances (
            user_id INTEGER PRIMARY KEY,
            balance INTEGER DEFAULT 1000,
            last_daily DATE,
            points INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            last_work TEXT,
            rank TEXT DEFAULT 'عضو'
        )
    ''')
    
    # جدول الأسئلة
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trivia_questions (
            id INTEGER PRIMARY KEY,
            question TEXT,
            option1 TEXT,
            option2 TEXT,
            option3 TEXT,
            option4 TEXT,
            correct_answer INTEGER
        )
    ''')
    
    conn.commit()
    conn.close()

# إضافة أسئلة عينة
def add_sample_questions():
    conn = sqlite3.connect('bot_data.db', check_same_thread=False)
    cursor = conn.cursor()
    
    questions = [
        ("ما هي عاصمة فرنسا؟", "لندن", "برلين", "باريس", "مدريد", 3),
        ("كم عدد الكواكب في النظام الشمسي؟", "7", "8", "9", "10", 2),
        ("ما هو العنصر الكيميائي للذهب؟", "Ag", "Fe", "Au", "Cu", 3),
        ("من كتب رواية 'البؤساء'؟", "تولستوي", "ديستويفسكي", "فيكتور هوغو", "شكسبير", 3),
        ("ما هو أطول نهر في العالم؟", "النيل", "الأمازون", "المسيسبي", "الدانوب", 1)
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO trivia_questions 
        (question, option1, option2, option3, option4, correct_answer)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', questions)
    
    conn.commit()
    conn.close()

init_db()
add_sample_questions()

# نظام البنك والألعاب
def get_user_balance(user_id):
    conn = sqlite3.connect('bot_data.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('SELECT balance, points, level, rank FROM user_balances WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return result[0], result[1], result[2], result[3]  # balance, points, level, rank
    else:
        # إنشاء حساب جديد للاعب
        conn = sqlite3.connect('bot_data.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO user_balances (user_id, balance, points, level, rank) VALUES (?, ?, ?, ?, ?)', 
                      (user_id, 1000, 0, 1, 'عضو'))
        conn.commit()
        conn.close()
        return 1000, 0, 1, 'عضو'

def update_user_balance(user_id, amount):
    balance, points, level, rank = get_user_balance(user_id)
    new_balance = balance + amount
    
    conn = sqlite3.connect('bot_data.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('UPDATE user_balances SET balance = ? WHERE user_id = ?', (new_balance, user_id))
    conn.commit()
    conn.close()
    
    return new_balance

def update_user_points(user_id, points_change):
    balance, points, level, rank = get_user_balance(user_id)
    new_points = points + points_change
    
    conn = sqlite3.connect('bot_data.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('UPDATE user_balances SET points = ? WHERE user_id = ?', (new_points, user_id))
    conn.commit()
    conn.close()
    
    return new_points

def update_user_rank(user_id, new_rank):
    conn = sqlite3.connect('bot_data.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('UPDATE user_balances SET rank = ? WHERE user_id = ?', (new_rank, user_id))
    conn.commit()
    conn.close()
    return new_rank

def can_work(user_id):
    conn = sqlite3.connect('bot_data.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('SELECT last_work FROM user_balances WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result and result[0]:
        last_work = datetime.fromisoformat(result[0])
        if datetime.now() - last_work < timedelta(hours=1):
            return False
    return True

# نظام الردود الآلية
def handle_auto_replies(message):
    text = message.text.lower().strip()
    
    # ردود الترحيب
    if text in ['السلام عليكم', 'سلام عليكم', 'السلام']:
        bot.reply_to(message, "وعليكم السلام حبيبي ❤️")
        return True
    
    elif text in ['هلا', 'هلا والله', 'اهلا']:
        bot.reply_to(message, "نورت ياعمري.. 😍")
        return True
    
    elif text in ['وي', 'واي', 'ويي']:
        bot.reply_to(message, "وي بالعسل نورتنا 😘")
        return True
    
    return False

# معالج جميع الرسائل النصية
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    text = message.text.lower().strip()
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    # معالجة الردود الآلية أولاً
    if handle_auto_replies(message):
        return
    
    # أمر البداية
    if text in ['بدء', 'start', 'اهلا', 'مرحبا']:
        user = message.from_user
        bot.reply_to(message, 
            f'مرحباً {user.first_name}! 👋\n'
            'أنا بوت متطور لإدارة المجموعات والألعاب 🎮\n'
            'اكتب "الاوامر" لرؤية جميع الأوامر المتاحة'
        )
    
    # عرض الأوامر
    elif text in ['الاوامر', 'اوامر', 'commands', 'مساعده', 'مساعدة']:
        commands_text = """
🎮 **أوامر الألعاب:**
بنك - عرض رصيدك ونقاطك
يومي - الحصول على المكافأة اليومية
مراهنة [المبلغ] - لعبة المراهنة
عمل - عمل ساعي (كل ساعة)

❓ **أوامر الأسئلة:**
سؤال - سؤال عشوائي بجوائز
اضف سؤال [السؤال|الخيار1|الخيار2|الخيار3|الخيار4|الإجابة] - إضافة سؤال جديد

🎯 **الألعاب:**
اكس او - لعبة X O مع البوت
حجر ورقة مقص [h/p/s] - لعبة حجر ورقة مقص
نرد - لعبة النرد
حظ - اختبار حظك

📊 **المعلومات:**
نقاطي - عرض نقاطك ومستواك
ترقية - ترقية مستواك
رتبتي - عرض رتبتك الحالية
الاوامر - عرض هذه القائمة

🛡️ **نظام الترقيات:**
ادمن - ترقية إلى ادمن
مدير - ترقية إلى مدير
منشئ - ترقية إلى منشئ
مميز - ترقية إلى مميز
ابلع - تنزيل كل الترقيات

🛡️ **الإدارة (للمشرفين):**
كتم [ثواني] - كتم مستخدم (بالرد)
الغاء كتم - إلغاء الكتم (بالرد)
حظر - حظر مستخدم (بالرد)
الغاء حظر - إلغاء الحظر (بالرد)
طرد - طرد مستخدم (بالرد)
مسح [عدد] - حذف رسائل

💬 **الردود الآلية:**
السلام عليكم - رد ترحيب
هلا - رد ترحيب
وي - رد ترحيب
        """
        bot.reply_to(message, commands_text)
    
    # أمر البنك
    elif text in ['بنك', 'رصيد', 'فلوس', 'balance']:
        balance, points, level, rank = get_user_balance(user_id)
        bot.reply_to(message, f"💰 رصيدك: {balance} قطعة ذهبية\n⭐ نقاطك: {points}\n📊 مستواك: {level}\n🎖️ رتبتك: {rank}")
    
    # الأمر اليومي
    elif text in ['يومي', 'مكافأة', 'daily']:
        user_id = message.from_user.id
        
        conn = sqlite3.connect('bot_data.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('SELECT last_daily FROM user_balances WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        
        now = datetime.now()
        
        if result and result[0]:
            last_daily = datetime.strptime(result[0], '%Y-%m-%d')
            if now.date() == last_daily.date():
                bot.reply_to(message, "❌ لقد حصلت على المكافأة اليومية بالفعل! عد غداً")
                conn.close()
                return
        
        # منح المكافأة
        reward = random.randint(100, 300)
        points_reward = random.randint(5, 15)
        new_balance = update_user_balance(user_id, reward)
        new_points = update_user_points(user_id, points_reward)
        
        cursor.execute('UPDATE user_balances SET last_daily = ? WHERE user_id = ?', (now.strftime('%Y-%m-%d'), user_id))
        conn.commit()
        conn.close()
        
        bot.reply_to(message, f"🎉 حصلت على {reward} ذهب و {points_reward} نقطة! رصيدك: {new_balance}")
    
    # أمر المراهنة
    elif text.startswith('مراهنة'):
        try:
            amount = int(text.split()[1])
            if amount <= 0:
                bot.reply_to(message, "❌ المبلغ يجب أن يكون موجباً")
                return
        except:
            bot.reply_to(message, "❌ استخدام خاطئ: مراهنة [المبلغ]")
            return
        
        user_id = message.from_user.id
        balance, points, level, rank = get_user_balance(user_id)
        
        if balance < amount:
            bot.reply_to(message, "❌ رصيدك غير كافي")
            return
        
        if random.random() < 0.5:
            win_amount = amount
            new_balance = update_user_balance(user_id, win_amount)
            new_points = update_user_points(user_id, 5)
            bot.reply_to(message, f"🎉 ربحت! فزت ب {win_amount} ذهب! رصيدك الجديد: {new_balance}")
        else:
            new_balance = update_user_balance(user_id, -amount)
            new_points = update_user_points(user_id, 2)
            bot.reply_to(message, f"💔 خسرت! خسرت {amount} ذهب. رصيدك الجديد: {new_balance}")
    
    # أمر العمل
    elif text in ['عمل', 'شغل', 'work']:
        user_id = message.from_user.id
        if not can_work(user_id):
            bot.reply_to(message, "⏰ انتظر ساعة قبل العمل مرة أخرى!")
            return
        
        earnings = random.randint(20, 100)
        points_earned = 5
        new_balance = update_user_balance(user_id, earnings)
        new_points = update_user_points(user_id, points_earned)
        
        conn = sqlite3.connect('bot_data.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('UPDATE user_balances SET last_work = ? WHERE user_id = ?', 
                      (datetime.now().isoformat(), user_id))
        conn.commit()
        conn.close()
        
        bot.reply_to(message, f"💼 عملت! +{earnings} ذهب +{points_earned} نقاط")
    
    # أمر النقاط
    elif text in ['نقاطي', 'نقاط', 'points']:
        balance, points, level, rank = get_user_balance(user_id)
        bot.reply_to(message, f"⭐ نقاطك: {points}\n📊 مستواك: {level}\n🎖️ رتبتك: {rank}")
    
    # أمر الترقية
    elif text in ['ترقية', 'levelup']:
        balance, points, level, rank = get_user_balance(user_id)
        required_points = 50 * level
        
        if points >= required_points:
            new_points = update_user_points(user_id, -required_points)
            conn = sqlite3.connect('bot_data.db', check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute('UPDATE user_balances SET level = level + 1 WHERE user_id = ?', (user_id,))
            conn.commit()
            conn.close()
            bot.reply_to(message, f"🎉 ترقية! المستوى الجديد: {level + 1}")
        else:
            bot.reply_to(message, f"❌ تحتاج {required_points} نقطة للترقية (لديك {points})")
    
    # أمر الرتبة
    elif text in ['رتبتي', 'رتبه', 'رتبة', 'رتب']:
        balance, points, level, rank = get_user_balance(user_id)
        bot.reply_to(message, f"🎖️ رتبتك الحالية: {rank}")
    
    # نظام الترقيات
    elif text == 'ادمن':
        new_rank = update_user_rank(user_id, 'ادمن')
        bot.reply_to(message, f"🎉 تمت ترقيتك إلى: {new_rank}")
    
    elif text == 'مدير':
        new_rank = update_user_rank(user_id, 'مدير')
        bot.reply_to(message, f"🎉 تمت ترقيتك إلى: {new_rank}")
    
    elif text == 'منشئ':
        new_rank = update_user_rank(user_id, 'منشئ')
        bot.reply_to(message, f"🎉 تمت ترقيتك إلى: {new_rank}")
    
    elif text == 'مميز':
        new_rank = update_user_rank(user_id, 'مميز')
        bot.reply_to(message, f"🎉 تمت ترقيتك إلى: {new_rank}")
    
    elif text == 'ابلع':
        new_rank = update_user_rank(user_id, 'عضو')
        bot.reply_to(message, f"📉 تم تنزيلك إلى: {new_rank}")
    
    # لعبة X O
    elif text in ['اكس او', 'xo', 'x o']:
        # يمكنك إضافة كود لعبة X O هنا
        bot.reply_to(message, "🎮 لعبة X O قريباً...")
    
    # لعبة حجر ورقة مقص
    elif text.startswith('حجر ورقة مقص'):
        user_id = message.from_user.id
        try:
            choice = text.split()[-1].lower()
        except:
            bot.reply_to(message, "❌ استخدام: حجر ورقة مقص [h=حجر, p=ورقة, s=مقص]")
            return
        
        choices = {'h': 'حجر', 'p': 'ورقة', 's': 'مقص'}
        if choice not in choices:
            bot.reply_to(message, "❌ اختيار غير صحيح! استخدم h, p, أو s")
            return
        
        bot_choice = random.choice(['h', 'p', 's'])
        user_choice_text = choices[choice]
        bot_choice_text = choices[bot_choice]
        
        if choice == bot_choice:
            result = "🤝 تعادل!"
            points = 3
        elif (choice == 'h' and bot_choice == 's') or (choice == 'p' and bot_choice == 'h') or (choice == 's' and bot_choice == 'p'):
            result = "🎉 فزت!"
            points = 10
            update_user_balance(user_id, 50)
        else:
            result = "💔 خسرت!"
            points = 1
        
        update_user_points(user_id, points)
        bot.reply_to(message, f"🎮 حجر ورقة مقص:\n\nاختيارك: {user_choice_text}\nاختيار البوت: {bot_choice_text}\n\n{result} (+{points} نقاط)")
    
    # لعبة النرد
    elif text in ['نرد', 'زهر', 'dice']:
        user_id = message.from_user.id
        user_dice = random.randint(1, 6)
        bot_dice = random.randint(1, 6)
        
        result_text = f"🎲 نردك: {user_dice}\n🤖 نرد البوت: {bot_dice}\n\n"
        
        if user_dice > bot_dice:
            win_amount = 30
            update_user_balance(user_id, win_amount)
            points = 8
            result_text += f"🎉 فزت! ربحت {win_amount} ذهب!"
        elif user_dice < bot_dice:
            points = 3
            result_text += f"💔 خسرت! حاول مرة أخرى."
        else:
            points = 5
            result_text += f"🤝 تعادل!"
        
        update_user_points(user_id, points)
        bot.reply_to(message, result_text + f" (+{points} نقاط)")
    
    # لعبة الحظ
    elif text in ['حظ', 'حظي', 'luck']:
        user_id = message.from_user.id
        luck = random.randint(1, 100)
        
        if luck <= 20:
            win_amount = random.randint(50, 200)
            update_user_balance(user_id, win_amount)
            points = 15
            result = f"🎉 حظ سعيد! فزت ب {win_amount} ذهب!"
        else:
            loss_amount = 50
            balance, points_curr, level, rank = get_user_balance(user_id)
            if balance >= loss_amount:
                update_user_balance(user_id, -loss_amount)
                result = f"💔 حظ سيء! خسرت {loss_amount} ذهب."
            else:
                result = "💔 حظ سيء! لكن رصيدك غير كافي للخسارة."
            points = 5
        
        update_user_points(user_id, points)
        bot.reply_to(message, f"🎰 لعبة الحظ:\n\n{result} (+{points} نقاط)")
    
    # أمر السؤال
    elif text in ['سؤال', 'اسئله', 'trivia']:
        # يمكنك إضافة كود الأسئلة هنا
        bot.reply_to(message, "❓ نظام الأسئلة قريباً...")
    
    # أوامر الإدارة (للمجموعات فقط)
    elif message.chat.type in ['group', 'supergroup']:
        # أمر الكتم
        if text.startswith('كتم') and message.reply_to_message:
            try:
                target_id = message.reply_to_message.from_user.id
                duration = 3600  # ساعة افتراضياً
                
                if len(text.split()) > 1:
                    duration = int(text.split()[1])
                
                bot.restrict_chat_member(chat_id, target_id, 
                                       until_date=int((datetime.now() + timedelta(seconds=duration)).timestamp()),
                                       permissions=types.ChatPermissions(can_send_messages=False))
                bot.reply_to(message, f"✅ كتم لـ {duration} ثانية")
            except Exception as e:
                bot.reply_to(message, f"❌ خطأ: {e}")
        
        # إلغاء الكتم
        elif text.startswith('الغاء كتم') and message.reply_to_message:
            try:
                target_id = message.reply_to_message.from_user.id
                bot.restrict_chat_member(chat_id, target_id,
                                       permissions=types.ChatPermissions(can_send_messages=True))
                bot.reply_to(message, "✅ إلغاء كتم")
            except Exception as e:
                bot.reply_to(message, f"❌ خطأ: {e}")
        
        # أمر الحظر
        elif text.startswith('حظر') and message.reply_to_message:
            try:
                target_id = message.reply_to_message.from_user.id
                bot.ban_chat_member(chat_id, target_id)
                bot.reply_to(message, "✅ تم الحظر")
            except Exception as e:
                bot.reply_to(message, f"❌ خطأ: {e}")
        
        # إلغاء الحظر
        elif text.startswith('الغاء حظر') and message.reply_to_message:
            try:
                target_id = message.reply_to_message.from_user.id
                bot.unban_chat_member(chat_id, target_id)
                bot.reply_to(message, "✅ إلغاء حظر")
            except Exception as e:
                bot.reply_to(message, f"❌ خطأ: {e}")
        
        # أمر الطرد
        elif text.startswith('طرد') and message.reply_to_message:
            try:
                target_id = message.reply_to_message.from_user.id
                bot.ban_chat_member(chat_id, target_id)
                bot.unban_chat_member(chat_id, target_id)
                bot.reply_to(message, "✅ تم الطرد")
            except Exception as e:
                bot.reply_to(message, f"❌ خطأ: {e}")
        
        # أمر المسح
        elif text.startswith('مسح'):
            try:
                count = int(text.split()[1]) if len(text.split()) > 1 else 5
                for i in range(count):
                    try:
                        bot.delete_message(chat_id, message.message_id - i - 1)
                    except:
                        pass
                bot.reply_to(message, f"✅ تم مسح {count} رسائل")
            except Exception as e:
                bot.reply_to(message, f"❌ خطأ: {e}")

# تشغيل البوت
if __name__ == '__main__':
    print("🤖 البوت المطور يعمل الآن...")
    print("📝 الآن يمكنك استخدام الأوامر بدون /")
    print("🎮 تم إضافة نظام الترقيات والردود الآلية!")
    bot.infinity_polling()
