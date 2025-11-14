import telebot
import time
import os
from gtts import gTTS
import random
from telebot.types import ChatMember
from telebot import types
from flask import Flask
import threading
import sqlite3
from datetime import datetime

# 🔧 إضافة Flask للاستضافة السحابية
app = Flask(__name__)

# ✅ إصلاح المتغيرات مع الإيدي الحقيقي
token = "8434698011:AAFI4P7_MGQvz8RMm9KjbOXIt-hKoMhThcc"
bot = telebot.TeleBot(token)

# ✅ تعريف المتغيرات مع الإيدي الحقيقي
admin_id = "8092119482"  # الإيدي الحقيقي
userk = [8092119482]     # الإيدي الحقيقي
locked_groups = []
muted_users = {}
locked_stickers = False

# ✅ تحديث كامل لبيانات المطور - بياناتك فقط
CHANNEL_USERNAME = "lofy_2000"  # بدون @
CHANNEL_URL = "https://t.me/lofy_2000"
developer_username = "@LOFY_25"
developer_channel = "@lofy_2000"

# ✅ قاعدة بيانات الهمسات
def init_whispers_db():
    conn = sqlite3.connect('whispers.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS whispers
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  sender_id INTEGER,
                  receiver_id INTEGER,
                  whisper_text TEXT,
                  group_id INTEGER,
                  timestamp TEXT)''')
    conn.commit()
    conn.close()

# ✅ زر المطور - رابط حسابك فقط
btn = types.InlineKeyboardButton(text='مطور السورس لوفي 𓅂', url="https://t.me/LOFY_25")

@app.route('/')
def home():
    return "✅ البوت يعمل بنجاح!"

@app.route('/health')
def health():
    return "🟢 Healthy", 200

# ✅ دالة التحقق إذا كان المستخدم مطور البوت
def is_developer(user_id):
    return str(user_id) == admin_id

# ✅ دالة التحقق إذا كان المستخدم مشرف أو مطور
def is_admin_or_developer(user_id, chat_id):
    if is_developer(user_id):
        return True
    try:
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ['administrator', 'creator']
    except:
        return False

# ✅ دالة التحقق من الاشتراك في القناة (معدلة)
def check_subscription(user_id):
    try:
        # ✅ المطور معفى دائماً من الاشتراك
        if is_developer(user_id):
            return True
            
        chat_member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return chat_member.status in ['member', 'administrator', 'creator']
    except:
        return False

# ✅ إنشاء زر الاشتراك في القناة
def create_subscription_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    subscribe_btn = types.InlineKeyboardButton(text="📢 اشترك في القناة", url=CHANNEL_URL)
    check_btn = types.InlineKeyboardButton(text="✅ تحقق من الاشتراك", callback_data="check_subscription")
    keyboard.add(subscribe_btn)
    keyboard.add(check_btn)
    return keyboard

# ✅ معالج callback للتحقق من الاشتراك
@bot.callback_query_handler(func=lambda call: call.data == "check_subscription")
def check_subscription_callback(call):
    user_id = call.from_user.id
    if check_subscription(user_id):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "🎉 شكراً للاشتراك! يمكنك الآن استخدام البوت.")
    else:
        bot.answer_callback_query(call.id, "❌ لم تشترك بعد في القناة!", show_alert=True)

# ✅ التحقق من الاشتراك قبل أي أمر
def subscription_required(func):
    def wrapper(message):
        user_id = message.from_user.id
        
        # ✅ استثناء الأوامر الأساسية والمطور
        if message.text in ["/start", "الاوامر"] or is_developer(user_id):
            return func(message)
            
        # ✅ التحقق من الاشتراك
        if not check_subscription(user_id):
            subscription_msg = f"""⚠️ عذراً، يجب الاشتراك في القناة أولاً

📢 قناة البوت الرسمية:
{CHANNEL_URL}

✅ بعد الاشتراك، اضغط على زر "تحقق من الاشتراك" """
            bot.send_message(
                message.chat.id, 
                subscription_msg, 
                reply_markup=create_subscription_keyboard(),
                parse_mode=None
            )
            return
        
        return func(message)
    return wrapper

# ✅ إنشاء قائمة الأوامر الرئيسية بالأزرار
def create_main_commands_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    btn_protection = types.InlineKeyboardButton("🛡️ أوامر الحماية", callback_data="commands_protection")
    btn_games = types.InlineKeyboardButton("🎮 الألعاب والترفيه", callback_data="commands_games")
    btn_fun = types.InlineKeyboardButton("💃 أوامر التسلية", callback_data="commands_fun")
    btn_other = types.InlineKeyboardButton("⚙️ أوامر متنوعة", callback_data="commands_other")
    btn_developer = types.InlineKeyboardButton("👑 أوامر المطور", callback_data="commands_developer")
    btn_whisper = types.InlineKeyboardButton("💌 نظام الهمسات", callback_data="commands_whisper")
    
    keyboard.add(btn_protection, btn_games)
    keyboard.add(btn_fun, btn_other)
    keyboard.add(btn_developer, btn_whisper)
    
    return keyboard

# ✅ معالج callback للأوامر الرئيسية
@bot.callback_query_handler(func=lambda call: call.data.startswith('commands_'))
def handle_commands_callback(call):
    user_id = call.from_user.id
    command_type = call.data.replace('commands_', '')
    
    if command_type == "protection":
        protection_commands_callback(call)
    elif command_type == "games":
        games_commands_callback(call)
    elif command_type == "fun":
        entertainment_commands_callback(call)
    elif command_type == "other":
        other_commands_callback(call)
    elif command_type == "developer":
        developer_commands_callback(call)
    elif command_type == "whisper":
        whisper_commands_callback(call)

@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    
    # ✅ المطور لا يحتاج للاشتراك
    if not check_subscription(user_id) and not is_developer(user_id):
        subscription_msg = f"""🎯 مرحباً {message.from_user.first_name}!

🤖 بوت حماية المجموعات المتقدم

⚠️ للاستخدام يجب الاشتراك في قناتنا أولاً:

📢 القناة الرسمية:
{CHANNEL_URL}

✅ بعد الاشتراك اضغط على زر التحقق"""
        bot.send_message(
            message.chat.id, 
            subscription_msg, 
            reply_markup=create_subscription_keyboard(),
            parse_mode=None
        )
        return
    
    # ✅ إذا كان مشترك أو مطور، عرض رسالة البداية
    brok = types.InlineKeyboardMarkup()
    brok.add(btn)
    
    # ✅ رسالة ترحيب خاصة للمطور
    if is_developer(user_id):
        start_text = f"""🎉 **مرحباً يا مطوري العزيز!** 👑

🤖 بوت حماية المجموعات المتقدم
⚡ الإصدار: 2.0 | المطور: {developer_username}

🛠️ **الأوامر المتاحة:**
• `الاوامر` - أوامر البوت الأساسية
• `مطور` - أوامر المطور الخاصة
• `معلومات` - معلومات البوت

🚀 **البوت جاهز للعمل!**"""
    else:
        start_text = f"""⌯︙أهلآ بك عزيزي 🙋‍♂
⌯︙اختصاص البوت حماية المجموعات 🔥
⌯︙لتفعيل البوت عليك اتباع مايلي 👇...
⌯︙اضف البوت الى مجموعتك 
⌯︙ارفعه ادمن (مشرف) 
⌯︙ارسل كلمة ( تفعيل ) ليتم تشغيل البوت في مجموعتك

👨‍💻 المطور: {developer_username}"""
    
    bot.reply_to(message, text=start_text, reply_markup=brok, parse_mode=None)

# ✅ تطبيق الاشتراك الإجباري على جميع الأوامر
@bot.message_handler(func=lambda message: message.text == "الاوامر")
@subscription_required
def show_commands(message):
    user_id = message.from_user.id
    
    # ✅ رسالة أوامر خاصة للمطور
    if is_developer(user_id):
        commands_text = f"""👑 **أوامر البوت - النسخة المطورة**

🛡️ **أوامر الحماية:** - حماية المجموعة من المخالفين
🎮 **أوامر الترفيه:** - ألعاب مسلية وتفاعلية  
💃 **أوامر التسلية:** - أوامر ترفيهية ومسلية
⚙️ **أوامر أخرى:** - أوامر متنوعة ومفيدة
💌 **نظام الهمسات:** - إرسال رسائل سرية

🛠️ **أوامر المطور:** - أوامر خاصة بالمطور

👨‍💻 **المطور: {developer_username}**"""
    else:
        commands_text = f"""⌯︙اهلا عزيزي الادمن 🧜🏻 .

🛡️ **أوامر الحماية** - حماية المجموعة
🎮 **الألعاب والترفيه** - ألعاب مسلية
💃 **أوامر التسلية** - أوامر ترفيهية
⚙️ **أوامر متنوعة** - أوامر مفيدة
💌 **نظام الهمسات** - رسائل سرية

⌯︙اضغط على الزر المناسب 👇

👨‍💻 المطور: {developer_username}"""
    
    bot.reply_to(message, commands_text, reply_markup=create_main_commands_keyboard(), parse_mode=None)

# ✅ أوامر الحماية بالأزرار
def protection_commands_callback(call):
    protection_text = f"""⌁︙اهلا عزيزي الادمن باوامر الحماية 🛡️ .
    
⌁︙حظر | (بالرد ) يحظر العضو 
⌁︙الغاء الحظر | (بالرد ) يلغي حظر العضو
⌁︙تقييد | ( بالرد ) يقييد العضو من الكتابة
⌁︙الغاء التقييد | ( بالرد ) يلغي تقييد العضو
⌁︙تقييد وقتي | ( بالرد ) يقييد العضو لمدة 10 دقائق
⌁︙تحذير | ( بالرد ) إذا تم تحذير الشخص ثلاث مرات يتم تقييده
⌁︙قفل الصور | يبدأ البوت بمسح الصور التي يرسلها الاعضاء
⌁︙فتح الصور | يتوقف البوت عن مسح الصور التي يرسلها الاعضاء
⌁︙قفل الملصقات | يبدأ البوت بمسح الملصقات التي يرسلها الاعضاء
⌁︙فتح الملصقات | يتوقف البوت عن مسح الملصقات التي يرسلها الاعضاء

⌁︙ يستطيع التحكم في هذه الأوامر المشرفين والأمنية في المجموعة ✅
⌁︙اضغط على اي امر لنسخه 👾 .

👨‍💻 المطور: {developer_username}"""
    
    keyboard = types.InlineKeyboardMarkup()
    back_btn = types.InlineKeyboardButton("🔙 رجوع", callback_data="back_to_main")
    keyboard.add(back_btn)
    
    bot.edit_message_text(protection_text, call.message.chat.id, call.message.message_id, reply_markup=keyboard, parse_mode=None)

# ✅ أوامر الألعاب بالأزرار
def games_commands_callback(call):
    games_text = f"""⌁︙اهلا عزيزي باوامر الالعاب 🎮🕹️ .
⌁︙نرد ↫يرسلك رقم من 1 الى 6 اذا طلع 6 انت فايز بس اذا طلع 5 او 4 او 3 او 2 او 1 تخسر 😔 .
⌁︙سلة ↫يرسل لك لعبة كرة السلة .
⌁︙كرة ↫يرسل لك لعبة كرة القدم .
⌁︙الاسرع ↫يرسل لك كلمة واسرع احد يكتبها يفوز .
- اضغط على اسم اللعبة للنسخ 👾 .

👨‍💻 المطور: {developer_username}"""
    
    keyboard = types.InlineKeyboardMarkup()
    back_btn = types.InlineKeyboardButton("🔙 رجوع", callback_data="back_to_main")
    keyboard.add(back_btn)
    
    bot.edit_message_text(games_text, call.message.chat.id, call.message.message_id, reply_markup=keyboard, parse_mode=None)

# ✅ أوامر التسلية بالأزرار
def entertainment_commands_callback(call):
    entertainment_text = f"""⌁︙اهلا عزيزي باوامر التسلية 💃🏻 .
⌁︙رد على الشخص من اجل استعمال الامر
⌁︙رفع حلو
⌁︙ذكائي
⌁︙غبائي
⌁︙تحبني
⌁︙همسة 💌 - إرسال رسالة سرية
⌁︙اضغط على اي وحدة لنسخها 👾 .
⌁︙الاوامر يقدر يستخدمها العضو عادي 💃🏻 .
⌁︙قريباً اوامر اكثر 😉 .

👨‍💻 المطور: {developer_username}"""
    
    keyboard = types.InlineKeyboardMarkup()
    whisper_btn = types.InlineKeyboardButton("💌 إرسال همسة", callback_data="send_whisper")
    back_btn = types.InlineKeyboardButton("🔙 رجوع", callback_data="back_to_main")
    keyboard.add(whisper_btn)
    keyboard.add(back_btn)
    
    bot.edit_message_text(entertainment_text, call.message.chat.id, call.message.message_id, reply_markup=keyboard, parse_mode=None)

# ✅ الأوامر المتنوعة بالأزرار
def other_commands_callback(call):
    other_text = f"""⌁︙اهلا عزيزي باوامر أخرى 🪗 .
⌁︙ايدي
⌁︙ايدي المجموعة
⌁︙الرابط
⌁︙المالك
⌁︙سورس
⌁︙السورس
⌁︙تفاعلي
⌁︙شعر
⌁︙سوره
⌁︙اوامر النطق 🔊... 
⌁︙انطق + الرسالة 
⌁︙مثال ( انطق مرحبا )
⌁︙اضغط على اي وحدة لنسخها 👾 .

👨‍💻 المطور: {developer_username}"""
    
    keyboard = types.InlineKeyboardMarkup()
    back_btn = types.InlineKeyboardButton("🔙 رجوع", callback_data="back_to_main")
    keyboard.add(back_btn)
    
    bot.edit_message_text(other_text, call.message.chat.id, call.message.message_id, reply_markup=keyboard, parse_mode=None)

# ✅ أوامر المطور بالأزرار
def developer_commands_callback(call):
    if not is_developer(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ هذا الأمر للمطور فقط!", show_alert=True)
        return
        
    dev_text = f"""🛠️ **أوامر المطور الخاصة**

• `معلومات` - عرض معلومات البوت
• `مجموعات` - عرض المجموعات النشطة
• `إحصائيات` - إحصائيات البوت
• `الهمسات` - عرض جميع همسات المجموعة

👑 **أنت المطور: {developer_username}**"""
    
    keyboard = types.InlineKeyboardMarkup()
    whispers_btn = types.InlineKeyboardButton("📋 عرض الهمسات", callback_data="show_whispers")
    back_btn = types.InlineKeyboardButton("🔙 رجوع", callback_data="back_to_main")
    keyboard.add(whispers_btn)
    keyboard.add(back_btn)
    
    bot.edit_message_text(dev_text, call.message.chat.id, call.message.message_id, reply_markup=keyboard, parse_mode=None)

# ✅ نظام الهمسات
def whisper_commands_callback(call):
    whisper_text = f"""💌 **نظام الهمسات السريعة**

**كيفية الاستخدام:**
1. اضغط على زر "إرسال همسة" 
2. قم بالرد على الشخص المراد إرسال الهمسة له
3. اكتب الهمسة السرية

**مميزات النظام:**
• 🔒 الهمسات سرية بين المرسل والمستقبل
• 👑 المطور يستطيع رؤية جميع الهمسات
• ⚡ سريعة وسهلة الاستخدام

👨‍💻 المطور: {developer_username}"""
    
    keyboard = types.InlineKeyboardMarkup()
    send_whisper_btn = types.InlineKeyboardButton("💌 إرسال همسة", callback_data="send_whisper")
    my_whispers_btn = types.InlineKeyboardButton("📨 همساتي", callback_data="my_whispers")
    back_btn = types.InlineKeyboardButton("🔙 رجوع", callback_data="back_to_main")
    
    keyboard.add(send_whisper_btn)
    keyboard.add(my_whispers_btn)
    keyboard.add(back_btn)
    
    bot.edit_message_text(whisper_text, call.message.chat.id, call.message.message_id, reply_markup=keyboard, parse_mode=None)

# ✅ زر الرجوع للقائمة الرئيسية
@bot.callback_query_handler(func=lambda call: call.data == "back_to_main")
def back_to_main_callback(call):
    user_id = call.from_user.id
    
    if is_developer(user_id):
        commands_text = f"""👑 **أوامر البوت - النسخة المطورة**

🛡️ **أوامر الحماية:** - حماية المجموعة من المخالفين
🎮 **أوامر الترفيه:** - ألعاب مسلية وتفاعلية  
💃 **أوامر التسلية:** - أوامر ترفيهية ومسلية
⚙️ **أوامر أخرى:** - أوامر متنوعة ومفيدة
💌 **نظام الهمسات:** - إرسال رسائل سرية

🛠️ **أوامر المطور:** - أوامر خاصة بالمطور

👨‍💻 **المطور: {developer_username}**"""
    else:
        commands_text = f"""⌯︙اهلا عزيزي الادمن 🧜🏻 .

🛡️ **أوامر الحماية** - حماية المجموعة
🎮 **الألعاب والترفيه** - ألعاب مسلية
💃 **أوامر التسلية** - أوامر ترفيهية
⚙️ **أوامر متنوعة** - أوامر مفيدة
💌 **نظام الهمسات** - رسائل سرية

⌯︙اضغط على الزر المناسب 👇

👨‍💻 المطور: {developer_username}"""
    
    bot.edit_message_text(commands_text, call.message.chat.id, call.message.message_id, 
                         reply_markup=create_main_commands_keyboard(), parse_mode=None)

# ✅ إرسال همسة جديدة
@bot.callback_query_handler(func=lambda call: call.data == "send_whisper")
def send_whisper_callback(call):
    instruction_text = f"""💌 **إرسال همسة سرية**

**الخطوات:**
1. قم **بالرد** على رسالة الشخص المراد إرسال الهمسة له
2. اكتب **همسة** متبوعاً برسالتك
3. مثال: `همسة أريد أن أخبرك سراً...`

**ملاحظة:** 
• الهمسة ستكون سرية بينك وبين المستقبل فقط
• المطور يستطيع رؤية جميع الهمسات

👨‍💻 المطور: {developer_username}"""
    
    keyboard = types.InlineKeyboardMarkup()
    back_btn = types.InlineKeyboardButton("🔙 رجوع", callback_data="commands_whisper")
    keyboard.add(back_btn)
    
    bot.edit_message_text(instruction_text, call.message.chat.id, call.message.message_id, reply_markup=keyboard, parse_mode=None)

# ✅ معالج رسائل الهمسات
@bot.message_handler(func=lambda message: message.text and message.text.startswith('همسة') and message.reply_to_message)
@subscription_required
def handle_whisper(message):
    try:
        if not message.reply_to_message:
            bot.reply_to(message, "❌ يجب الرد على الشخص المراد إرسال الهمسة له!")
            return
        
        sender_id = message.from_user.id
        receiver_id = message.reply_to_message.from_user.id
        group_id = message.chat.id
        
        # منع إرسال همسة للنفس
        if sender_id == receiver_id:
            bot.reply_to(message, "❌ لا يمكنك إرسال همسة لنفسك!")
            return
        
        # استخراج نص الهمسة
        whisper_text = message.text.replace('همسة', '').strip()
        if not whisper_text:
            bot.reply_to(message, "❌ يرجى كتابة نص الهمسة بعد كلمة 'همسة'")
            return
        
        # حفظ الهمسة في قاعدة البيانات
        conn = sqlite3.connect('whispers.db')
        c = conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        c.execute("INSERT INTO whispers (sender_id, receiver_id, whisper_text, group_id, timestamp) VALUES (?, ?, ?, ?, ?)",
                 (sender_id, receiver_id, whisper_text, group_id, timestamp))
        conn.commit()
        conn.close()
        
        # إرسال تأكيد للمرسل
        bot.reply_to(message, "✅ تم إرسال الهمسة السرية بنجاح!")
        
        # إرسال إشعار للمستقبل (فقط إذا كان في المجموعة)
        try:
            receiver_name = message.reply_to_message.from_user.first_name
            notification_text = f"💌 لديك همسة سرية جديدة من {message.from_user.first_name}\n\nاستخدم زر 'همساتي' لعرضها!"
            
            keyboard = types.InlineKeyboardMarkup()
            view_whispers_btn = types.InlineKeyboardButton("📨 عرض همساتي", callback_data="my_whispers")
            keyboard.add(view_whispers_btn)
            
            bot.send_message(receiver_id, notification_text, reply_markup=keyboard)
        except:
            pass  # لا يمكن إرسال رسالة خاصة إذا لم يبدأ المستخدم محادثة مع البوت
            
    except Exception as e:
        bot.reply_to(message, "❌ حدث خطأ في إرسال الهمسة!")

# ✅ عرض الهمسات الخاصة بالمستخدم
@bot.callback_query_handler(func=lambda call: call.data == "my_whispers")
def show_my_whispers(call):
    user_id = call.from_user.id
    
    conn = sqlite3.connect('whispers.db')
    c = conn.cursor()
    
    # جلب الهمسات المرسلة والمستلمة
    c.execute("SELECT * FROM whispers WHERE sender_id = ? OR receiver_id = ? ORDER BY timestamp DESC LIMIT 10", (user_id, user_id))
    whispers = c.fetchall()
    conn.close()
    
    if not whispers:
        no_whispers_text = f"""📭 **لا توجد همسات**

لم تستلم أو ترسل أي همسات بعد.

💌 لإرسال همسة:
1. اضغط على زر "إرسال همسة"
2. قم بالرد على الشخص
3. اكتب 'همسة' متبوعاً برسالتك

👨‍💻 المطور: {developer_username}"""
        
        keyboard = types.InlineKeyboardMarkup()
        send_btn = types.InlineKeyboardButton("💌 إرسال همسة", callback_data="send_whisper")
        back_btn = types.InlineKeyboardButton("🔙 رجوع", callback_data="commands_whisper")
        keyboard.add(send_btn)
        keyboard.add(back_btn)
        
        bot.edit_message_text(no_whispers_text, call.message.chat.id, call.message.message_id, reply_markup=keyboard, parse_mode=None)
        return
    
    whispers_text = f"""📨 **همساتي** - آخر 10 همسات

"""
    
    for whisper in whispers:
        whisper_id, sender_id, receiver_id, text, group_id, timestamp = whisper
        
        if user_id == sender_id:
            direction = "📤 أرسلت إلى"
            target_id = receiver_id
        else:
            direction = "📥 استلمت من"
            target_id = sender_id
        
        try:
            user_info = bot.get_chat(target_id)
            target_name = user_info.first_name
        except:
            target_name = "مستخدم"
        
        date = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").strftime("%H:%M %d/%m")
        whispers_text += f"**{direction} {target_name}:**\n{text}\n⏰ {date}\n\n"
    
    whispers_text += f"\n👨‍💻 المطور: {developer_username}"
    
    keyboard = types.InlineKeyboardMarkup()
    send_btn = types.InlineKeyboardButton("💌 إرسال همسة", callback_data="send_whisper")
    refresh_btn = types.InlineKeyboardButton("🔄 تحديث", callback_data="my_whispers")
    back_btn = types.InlineKeyboardButton("🔙 رجوع", callback_data="commands_whisper")
    keyboard.add(send_btn, refresh_btn)
    keyboard.add(back_btn)
    
    bot.edit_message_text(whispers_text, call.message.chat.id, call.message.message_id, reply_markup=keyboard, parse_mode=None)

# ✅ عرض جميع الهمسات للمطور
@bot.callback_query_handler(func=lambda call: call.data == "show_whispers")
def show_all_whispers(call):
    if not is_developer(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ هذا الأمر للمطور فقط!", show_alert=True)
        return
    
    conn = sqlite3.connect('whispers.db')
    c = conn.cursor()
    c.execute("SELECT * FROM whispers ORDER BY timestamp DESC LIMIT 20")
    all_whispers = c.fetchall()
    conn.close()
    
    if not all_whispers:
        bot.answer_callback_query(call.id, "❌ لا توجد همسات في قاعدة البيانات!", show_alert=True)
        return
    
    whispers_text = "👑 **جميع الهمسات - للمطور فقط**\n\n"
    
    for whisper in all_whispers:
        whisper_id, sender_id, receiver_id, text, group_id, timestamp = whisper
        
        try:
            sender_info = bot.get_chat(sender_id)
            sender_name = sender_info.first_name
        except:
            sender_name = "مستخدم"
        
        try:
            receiver_info = bot.get_chat(receiver_id)
            receiver_name = receiver_info.first_name
        except:
            receiver_name = "مستخدم"
        
        date = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").strftime("%H:%M %d/%m")
        whispers_text += f"**من:** {sender_name} ({sender_id})\n"
        whispers_text += f"**إلى:** {receiver_name} ({receiver_id})\n"
        whispers_text += f"**الهمسة:** {text}\n"
        whispers_text += f"**الوقت:** {date}\n"
        whispers_text += "─" * 30 + "\n\n"
    
    # إذا كانت الرسالة طويلة جداً، نقسمها
    if len(whispers_text) > 4000:
        parts = [whispers_text[i:i+4000] for i in range(0, len(whispers_text), 4000)]
        for part in parts:
            bot.send_message(call.from_user.id, part, parse_mode=None)
    else:
        bot.send_message(call.from_user.id, whispers_text, parse_mode=None)
    
    bot.answer_callback_query(call.id, "✅ تم إرسال جميع الهمسات في الخاص!")

# ✅ الأوامر الحالية تبقى كما هي (التفعيل، الحماية، الألعاب، إلخ)
@bot.message_handler(func=lambda message: message.text == "تفعيل")
@subscription_required
def activate_bot(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    if is_admin_or_developer(user_id, chat_id):
        if chat_id not in locked_groups:
            locked_groups.append(chat_id)
        
        # ✅ رسالة تفعيل خاصة للمطور
        if is_developer(user_id):
            activation_text = f"""✅ **تم تفعيل البوت بنجاح**

⚡ التفعيل بواسطة: المطور
📌 المجموعة: {chat_id}
🔢 المجموعات النشطة: {len(locked_groups)}

👑 **المطور: {developer_username}**"""
        else:
            activation_text = f"""- تـم تفعيل البوت بنجاح ✅

• ارسل (الاوامر) لمعرفة اوامر البوت 💯

👨‍💻 المطور: {developer_username}"""
        
        bot.reply_to(message, activation_text, parse_mode=None)
    else:
        bot.reply_to(message, "⌁︙انت مو ادمن ياعضو 💃🏻 !", parse_mode=None)

# ... (بقية الأوامر الحالية تبقى كما هي بدون تغيير)
# [يتبع باقي الكود الحالي بدون تغيير]

# ✅ تشغيل البوت مع Flask
def run_flask():
    app.run(host='0.0.0.0', port=8080)

def run_bot():
    # تهيئة قاعدة بيانات الهمسات
    init_whispers_db()
    
    while True:
        try:
            print("🤖 البوت يعمل بنجاح...")
            bot.polling(none_stop=True)
        except Exception as e:
            print(f"❌ خطأ: {e}")
            time.sleep(5)

if __name__ == "__main__":
    # ✅ تشغيل Flask في thread منفصل
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # ✅ تشغيل البوت
    print("🚀 بدء تشغيل البوت...")
    run_bot()
