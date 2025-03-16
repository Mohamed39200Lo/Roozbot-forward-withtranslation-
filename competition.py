import telebot
import json
import os
import re
import random
import threading
import traceback
from datetime import datetime, timedelta
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from app import server
import requests  # لإضافة التفاعل مع GitHub Gist

# استبدل بـ token البوت الخاص بك
TOKEN = "7710195977:AAEiamn8qPONy90CxvmS29iWXv8f1rFUBEU"
bot = telebot.TeleBot(TOKEN)

# تحميل البيانات من الملف
token_part1 = "ghp_gFkAlF"
token_part2 = "A4sbNyuLtX"
token_part3 = "YvqKfUEBHXNaPh3ABRms"

# دمج الأجزاء للحصول على التوكن الكامل
GITHUB_TOKEN = token_part1 + token_part2 + token_part3
GIST_ID = "1050e1f10d7f5591f4f26ca53f2189e9"

processed_media_groups = set()

# تحميل البيانات من Gist
def load_data():
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(f"https://api.github.com/gists/{GIST_ID}", headers=headers)
    if response.status_code == 200:
        files = response.json().get('files', {})
        content = files.get('dataمسابقة.json', {}).get('content', '{}')
        return json.loads(content)
    else:
        return {}

# حفظ البيانات في الملف
def save_data(data):
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}"
    }
    payload = {
        "files": {
            "dataمسابقة.json": {
                "content": json.dumps(data, indent=4, default=str)
            }
        }
    }
    response = requests.patch(f"https://api.github.com/gists/{GIST_ID}", headers=headers, json=payload)
    if response.status_code != 200:
        print(f"Failed to update Gist: {response.status_code}, {response.text}")

# تحميل بيانات البوت
bot_data = load_data()

# الحصول على بيانات المستخدم أو إنشائها إذا لم تكن موجودة
def get_user_data(user_id, username):
    user_id = str(user_id)
    
    if user_id not in bot_data:
        bot_data[user_id] = {
            "username": username,
            "image": None,
            "button_text": None,
            "channels": [],
            "winners_count": None,
            "selected_channel": None,
            "publish_date": None,
            "result_time": None,
            "giveaways": [],
            "current_operation": None  # إضافة حقل لتتبع العملية الجارية
        }
    else:
        bot_data[user_id]["username"] = username

    return bot_data[user_id]

# إلغاء العملية الحالية
def cancel_operation(user_id):
    user_id = str(user_id)
    if user_id in bot_data:
        bot_data[user_id]["image"] = None
        bot_data[user_id]["button_text"] = None
        bot_data[user_id]["winners_count"] = None
        bot_data[user_id]["selected_channel"] = None
        bot_data[user_id]["publish_date"] = None
        bot_data[user_id]["result_time"] = None
        bot_data[user_id]["current_operation"] = None  # إعادة تعيين العملية الجارية
        save_data(bot_data)

# دالة لمعالجة الأخطاء
def handle_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"⚠️ حدث خطأ في الدالة {func.__name__}: {str(e)}")
            traceback.print_exc()
    return wrapper

# أمر البدء
@bot.message_handler(commands=['start'])
@handle_errors
def start(message):
    user_id = message.from_user.id
    username = message.from_user.username or f"User_{user_id}"
    
    # إلغاء أي عملية جارية
    cancel_operation(user_id)
    
    get_user_data(user_id, username)
    save_data(bot_data)

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🎁 إنشاء هدية", callback_data="create_giveaway"))
    markup.add(InlineKeyboardButton("📜 قائمة الهدايا", callback_data="list_giveaways"))
    markup.add(InlineKeyboardButton("📡 قنواتي", callback_data="my_channels"))

    bot.send_message(message.chat.id, "مرحبًا بكم! 👋\n سيساعدك الروبوت الخاص بنا في إجراء عملية توزيع هدايا على قناتك \n هل انت مستعد لإنشاء هدية جديدة؟", reply_markup=markup)

# زر الرجوع
def back_button():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("⬅️ الرجوع", callback_data="main_menu"))
    return markup

# إنشاء هدية
@bot.callback_query_handler(func=lambda call: call.data == "create_giveaway")
@handle_errors
def create_giveaway(call):
    user_id = str(call.from_user.id)
    bot_data[user_id]["current_operation"] = "create_giveaway"
    save_data(bot_data)
    
    bot.send_message(call.message.chat.id, "🎁 *إنشاء هدية*\n\n"
                                       "**ارسل رسالة نصية للسحب، يمكنك أيضًا إرسال صورة أو مقطع فيديو أو صورة GIF مع النص.**\n\n"
                                       "*يمكنك استخدام ملف وسائط واحد فقط.*\n\n"
                                       "**بوت إجراء المسابقات مجاني تمامًا وشفاف وبدون إعلانات، وسيسعد إذا قمت بالإشارة إلى رابط له في منشور المسابقة. شكرًا لك @RooGiftsBot**",                     
                 parse_mode="Markdown")
    bot.register_next_step_handler(call.message, save_giveaway_image)

# حفظ صورة الهدية
@handle_errors
def save_giveaway_image(message):
    user_id = str(message.from_user.id)
    
    # التحقق من إلغاء العملية
    if bot_data.get(user_id, {}).get("current_operation") != "create_giveaway":
        bot.send_message(message.chat.id, "⚠️ تم إلغاء العملية الحالية. الرجاء البدء من جديد باستخدام /start.")
        return
    
    if message.photo:
        file_id = message.photo[-1].file_id
        bot_data[user_id]["image"] = file_id
        save_data(bot_data)
        bot.send_message(message.chat.id, "✅ تم إضافة الصورة بنجاح!")
    else:
        bot.send_message(message.chat.id, "⚠️ الرجاء إرسال صورة صالحة!")

    bot.send_message(message.chat.id, "🔹 *ارسل النص الذي سيظهر على الزر:*", parse_mode="Markdown")
    bot.register_next_step_handler(message, save_button_text)

# حفظ نص الزر
@handle_errors
def save_button_text(message):
    user_id = str(message.from_user.id)
    
    # التحقق من إلغاء العملية
    if bot_data.get(user_id, {}).get("current_operation") != "create_giveaway":
        bot.send_message(message.chat.id, "⚠️ تم إلغاء العملية الحالية. الرجاء البدء من جديد باستخدام /start.")
        return
    
    bot_data[user_id]["button_text"] = message.text
    save_data(bot_data)
    bot.send_message(message.chat.id, f"✅ تم حفظ نص الزر: {message.text}")

    bot.send_message(message.chat.id, "**اضف القنوات التي سيحتاج المستخدمون الى الاشتراك فيها للمشاركة في المسابقة.**\n"
                                      "*الاشتراك في القناة التي تقام فيها المسابقة إلزامي ويتم تمكينة افتراضياً\n\n*"
                                      "لإضافة قناة يجب عليك:\n"
                                      "1. اضف البوت (@RooGiftsBot) الى قناتك كمسؤول  (هذا ضروري حتي يتمكن البوت من التحقق مما إذا كان المستخدم مشتركاً في القناة).  \n"
                                      "2. ارسل القناة الي الروبوت بتنسيق  @channelname (أو قم بأعادة توجيه رسالة من القناة) . \n",
                     parse_mode="Markdown")
    bot.register_next_step_handler(message, add_channels)

# إضافة القنوات
@handle_errors
def add_channels(message):
    user_id = str(message.from_user.id)
    
    # التحقق من إلغاء العملية
    if bot_data.get(user_id, {}).get("current_operation") != "create_giveaway":
        bot.send_message(message.chat.id, "⚠️ تم إلغاء العملية الحالية. الرجاء البدء من جديد باستخدام /start.")
        return
    
    channel_username = message.text.strip()

    if not channel_username.startswith("@") and not re.match(r'https?://', channel_username):
        bot.send_message(message.chat.id, "⚠️ التنسيق غير صالح! الرجاء إرسال القناة بصيغة @channelname أو كرابط.")
        bot.register_next_step_handler(message, add_channels)
        return

    bot_data[user_id]["channels"].append(channel_username)
    save_data(bot_data)
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("➕ إضافة قناة أخرى", callback_data="add_another_channel"))
    markup.add(InlineKeyboardButton("✅ استمرار", callback_data="continue_to_winners"))
    
    bot.send_message(message.chat.id, "✅ تم إضافة القناة بنجاح! ماذا تريد أن تفعل الآن؟", reply_markup=markup)

# إضافة قناة أخرى
@bot.callback_query_handler(func=lambda call: call.data == "add_another_channel")
@handle_errors
def add_another_channel(call):
    bot.send_message(call.message.chat.id, "🔹 *يرجى إرسال القناة الإضافية بنفس التنسيق:* @channelname", parse_mode="Markdown")
    bot.register_next_step_handler(call.message, add_channels)

# الاستمرار إلى اختيار الفائزين
@bot.callback_query_handler(func=lambda call: call.data == "continue_to_winners")
@handle_errors
def continue_to_winners(call):
    bot.send_message(call.message.chat.id, "🔹 *كم عدد الفائزين الذين يجب على الروبوت اختيارهم؟*", parse_mode="Markdown")
    bot.register_next_step_handler(call.message, set_winners_count)

# تعيين عدد الفائزين
@handle_errors
def set_winners_count(message):
    user_id = str(message.from_user.id)
    
    # التحقق من إلغاء العملية
    if bot_data.get(user_id, {}).get("current_operation") != "create_giveaway":
        bot.send_message(message.chat.id, "⚠️ تم إلغاء العملية الحالية. الرجاء البدء من جديد باستخدام /start.")
        return
    
    if not message.text.isdigit():
        bot.send_message(message.chat.id, "⚠️ الرجاء إرسال رقم صحيح.")
        bot.register_next_step_handler(message, set_winners_count)
        return

    bot_data[user_id]["winners_count"] = int(message.text)
    save_data(bot_data)
    
    bot.send_message(message.chat.id, f"✅ تم تسجيل عدد الفائزين: {message.text}")

    markup = InlineKeyboardMarkup()
    for channel in bot_data[user_id]["channels"]:
        markup.add(InlineKeyboardButton(channel, callback_data=f"select_channel_{channel}"))

    bot.send_message(message.chat.id, "🔹 *على أي قناة تنشر المسابقة؟*", parse_mode="Markdown", reply_markup=markup)
    
# اختيار القناة
@bot.callback_query_handler(func=lambda call: call.data.startswith("select_channel_"))
@handle_errors
def select_channel(call):
    user_id = str(call.from_user.id)
    selected_channel = call.data.replace("select_channel_", "")
    bot_data[user_id]["selected_channel"] = selected_channel
    save_data(bot_data)

    bot.send_message(call.message.chat.id, f"✅ تم اختيار القناة: {selected_channel}")

    bot.send_message(call.message.chat.id, "🔹 *متى يجب أن أنشر الهدية؟ (يرجى إرسال التاريخ بتنسيق YYYY-MM-DD HH:MM)*",
                     parse_mode="Markdown")
    bot.register_next_step_handler(call.message, set_publish_date)

# تعيين تاريخ النشر
from datetime import datetime, timedelta  # تأكد من استيراد timedelta



# تعيين تاريخ النشر
@handle_errors
def set_publish_date(message):
    user_id = str(message.from_user.id)
    
    # التحقق من إلغاء العملية
    if bot_data.get(user_id, {}).get("current_operation") != "create_giveaway":
        bot.send_message(message.chat.id, "⚠️ تم إلغاء العملية الحالية. الرجاء البدء من جديد باستخدام /start.")
        return
    
    date_pattern = r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$"

    if not re.match(date_pattern, message.text):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("⬅️ الرجوع إلى القائمة الرئيسية", callback_data="main_menu"))
        
        bot.send_message(message.chat.id, "⚠️ التنسيق خطأ! الرجاء إرسال التاريخ بتنسيق YYYY-MM-DD HH:MM\n\n"
                                         "اضغط على الزر أدناه للعودة إلى القائمة الرئيسية:", reply_markup=markup)
        bot.register_next_step_handler(message, set_publish_date)
        return

    # تحويل التاريخ المدخل إلى كائن datetime
    user_time = datetime.strptime(message.text, "%Y-%m-%d %H:%M")
    
    # طرح 3 ساعات من التوقيت المدخل
    adjusted_time = user_time - timedelta(hours=3)
    
    # حفظ التوقيت المعدل
    bot_data[user_id]["publish_date"] = adjusted_time.strftime("%Y-%m-%d %H:%M")
    save_data(bot_data)
    
    bot.send_message(message.chat.id, "✅ تم حفظ تاريخ النشر بعد تعديله ليتناسب مع توقيت الاستضافة!")

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("2 دقائق", callback_data="result_time_2min"))
    markup.add(InlineKeyboardButton("10 دقائق", callback_data="result_time_10min"))
    markup.add(InlineKeyboardButton("ساعة", callback_data="result_time_1hour"))
    markup.add(InlineKeyboardButton("يوم", callback_data="result_time_1day"))

    bot.send_message(message.chat.id, "🔹 *ما التوقيت الذي تريده لإعلان نتيجة السحب؟*", 
                     parse_mode="Markdown", reply_markup=markup)



# تعيين وقت النتيجة
@bot.callback_query_handler(func=lambda call: call.data.startswith("result_time_"))
@handle_errors
def set_result_time(call):
    user_id = str(call.from_user.id)
    time_option = call.data.replace("result_time_", "")
    
    time_values = {
        "2min": 2,
        "10min": 10,
        "1hour": 60,
        "1day": 1440
    }
    
    time_text = {
        "2min": "دقيقتان",
        "10min": "10 دقائق",
        "1hour": "ساعة واحدة",
        "1day": "يوم واحد"
    }
    
    bot_data[user_id]["result_time"] = {
        "value": time_values[time_option],
        "text": time_text[time_option]
    }
    save_data(bot_data)
    
    bot.send_message(call.message.chat.id, f"✅ تم تحديد وقت إعلان النتيجة: {time_text[time_option]}")
    
    winners_count = bot_data[user_id]["winners_count"]
    publish_date = bot_data[user_id]["publish_date"]
    result_time_text = bot_data[user_id]["result_time"]["text"]
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✅ تأكيد", callback_data="confirm_giveaway"))
    markup.add(InlineKeyboardButton("❌ حذف", callback_data="delete_giveaway"))

    bot.send_message(call.message.chat.id, f"✅ *تأكد من السحب مرة أخرى*\n\n"
                                      f"📅 سيتم الانتهاء من القرعة بتاريخ: *{publish_date}*\n"
                                      f"🏆 عدد الفائزين: *{winners_count}*\n"
                                      f"⏱ وقت إعلان النتيجة: *{result_time_text}* من وقت النشر\n\n"
                                      "يرجى تأكيد أو حذف المسابقة.", 
                     parse_mode="Markdown", reply_markup=markup)

# تأكيد المسابقة
@bot.callback_query_handler(func=lambda call: call.data == "confirm_giveaway")
@handle_errors
def confirm_giveaway(call):
    user_id = str(call.from_user.id)
    
    giveaway = {
        "image": bot_data[user_id]["image"],
        "button_text": bot_data[user_id]["button_text"],
        "channels": bot_data[user_id]["channels"],
        "winners_count": bot_data[user_id]["winners_count"],
        "selected_channel": bot_data[user_id]["selected_channel"],
        "publish_date": bot_data[user_id]["publish_date"],
        "result_time": bot_data[user_id]["result_time"],
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "pending",
        "participants": []
    }
    
    if "giveaways" not in bot_data[user_id]:
        bot_data[user_id]["giveaways"] = []
    
    bot_data[user_id]["giveaways"].append(giveaway)
    save_data(bot_data)
    
    # نشر منشور المسابقة
    publish_giveaway(user_id, len(bot_data[user_id]["giveaways"]) - 1)
    
    bot.send_message(call.message.chat.id, "🎉 تم حفظ المسابقة وجاري تجهيزها للنشر.\n"
                                           "سيتم نشر النتائج تلقائيًا على القناة المختارة بعد الوقت المحدد.\n\n"
                                           "للرجوع إلى القائمة الرئيسية اضغط /start", parse_mode="Markdown")

# نشر منشور المسابقة
@handle_errors
def publish_giveaway(user_id, giveaway_idx):
    giveaway = bot_data[user_id]["giveaways"][giveaway_idx]
    channel = giveaway["selected_channel"]

    # حساب وقت النتيجة
    publish_date = datetime.strptime(giveaway["publish_date"], "%Y-%m-%d %H:%M")
    result_minutes = giveaway["result_time"]["value"]
    result_time = publish_date + timedelta(minutes=result_minutes)

    # إنشاء منشور المسابقة مع الصورة والنص
    giveaway_message = f"🎉 *مسابقة جديدة!*\n\n" \
                       f"🎁 الوصف: {giveaway['button_text']}\n" \
                       f"🏆 عدد الفائزين: {giveaway['winners_count']}\n" \
                       f"📅 تاريخ النشر: {giveaway['publish_date']}\n" \
                       f"⏱ تاريخ إعلان النتائج: {result_time.strftime('%Y-%m-%d %H:%M')}\n\n" \
                       f"سيتم اختيار الفائزين عشوائيًا من أعضاء القناة."

    try:
        # إرسال منشور المسابقة مع الصورة
        if giveaway["image"]:
            message = bot.send_photo(channel, giveaway["image"], caption=giveaway_message, parse_mode="Markdown")
        else:
            message = bot.send_message(channel, giveaway_message, parse_mode="Markdown")
        
        # إضافة زر المشاركة
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🎁 انضم إلى المسابقة", callback_data=f"join_giveaway_{giveaway_idx}"))
        bot.edit_message_reply_markup(channel, message.message_id, reply_markup=markup)
        
        bot.send_message(user_id, f"✅ تم نشر المسابقة بنجاح على القناة {channel}")
    except telebot.apihelper.ApiException as e:
        if "chat not found" in str(e):
            bot.send_message(user_id, f"⚠️ حدث خطأ: البوت ليس عضوًا في القناة أو المجموعة المحددة ({channel}). يرجى إضافته وإعطائه الصلاحيات اللازمة.")
        else:
            bot.send_message(user_id, f"⚠️ حدث خطأ أثناء نشر المسابقة: {str(e)}")

    # جدولة إعلان النتائج
    schedule_giveaway_result(user_id, giveaway_idx)

# الانضمام إلى المسابقة
@bot.callback_query_handler(func=lambda call: call.data.startswith("join_giveaway_"))
@handle_errors
def join_giveaway(call):
    giveaway_idx = int(call.data.replace("join_giveaway_", ""))
    
    user_id = str(call.from_user.id)
    username = call.from_user.username or f"User_{user_id}"
    
    # البحث عن المسابقة المحددة
    giveaway_found = False
    for user_data in bot_data.values():
        if "giveaways" in user_data:
            for idx, giveaway in enumerate(user_data["giveaways"]):
                if idx == giveaway_idx:
                    giveaway_found = True
                    break
            if giveaway_found:
                break
    
    if not giveaway_found:
        bot.answer_callback_query(call.id, "⚠️ المسابقة غير موجودة.")
        return

    # التحقق من الاشتراك في القنوات
    required_channels = giveaway["channels"]
    user_is_subscribed = True

    for channel in required_channels:
        try:
            chat_member = bot.get_chat_member(channel, call.from_user.id)
            if chat_member.status not in ["member", "administrator", "creator"]:
                user_is_subscribed = False
                break
        except Exception as e:
            user_is_subscribed = False
            break

    if not user_is_subscribed:
        bot.answer_callback_query(call.id, "⚠️ يجب أن تكون مشتركًا في جميع القنوات المطلوبة للمشاركة في المسابقة.")
        return

    # إضافة المشارك
    if user_id not in [p["user_id"] for p in giveaway["participants"]]:
        giveaway["participants"].append({
            "user_id": user_id,
            "username": username
        })
        save_data(bot_data)
        bot.answer_callback_query(call.id, "✅ تم الانضمام إلى المسابقة بنجاح!")
    else:
        bot.answer_callback_query(call.id, "⚠️ أنت بالفعل مشارك في هذه المسابقة.")

# جدولة إعلان النتائج
@handle_errors
def schedule_giveaway_result(user_id, giveaway_idx):
    try:
        giveaway = bot_data[user_id]["giveaways"][giveaway_idx]
        channel = giveaway["selected_channel"]

        publish_date = datetime.strptime(giveaway["publish_date"], "%Y-%m-%d %H:%M")
        result_minutes = giveaway["result_time"]["value"]
        result_time = publish_date + timedelta(minutes=result_minutes)

        def post_results():
            try:
                if not giveaway["participants"]:
                    bot.send_message(user_id, "⚠️ لا يوجد مشاركين في المسابقة لاختيار الفائزين.")
                    return

                unique_participants = []
                seen_user_ids = set()

                for participant in giveaway["participants"]:
                    if isinstance(participant, str):
                        user_id_winner = participant
                        if user_id_winner not in seen_user_ids:
                            seen_user_ids.add(user_id_winner)
                            unique_participants.append({"user_id": user_id_winner, "username": None})
                    elif isinstance(participant, dict):
                        user_id_winner = participant["user_id"]
                        if user_id_winner not in seen_user_ids:
                            seen_user_ids.add(user_id_winner)
                            unique_participants.append(participant)
                    else:
                        continue

                winners_count = min(giveaway["winners_count"], len(unique_participants))
                winners = random.sample(unique_participants, winners_count)

                winners_message = "🎉 *نتائج المسابقة*\n\n🏆 الفائزون:\n"
                valid_winners = []

                for winner in winners:
                    try:
                        user_id_winner = winner["user_id"]
                        username = winner["username"]
                        if not username:
                            user = bot.get_chat_member(channel, user_id_winner).user
                            username = user.username or user.first_name
                        valid_winners.append(f"@{username}" if username else user_id_winner)
                    except Exception as e:
                        continue

                if not valid_winners:
                    bot.send_message(user_id, "⚠️ لا يمكن العثور على أي فائزين صالحين.")
                    return

                winners_message += ", ".join(valid_winners) + "\n\nتهانينا للفائزين! 🎊"

                giveaway["status"] = "completed"
                giveaway["winners"] = valid_winners
                save_data(bot_data)

                bot.send_message(channel, winners_message, parse_mode="Markdown")
                bot.send_message(user_id, f"✅ تم إعلان النتائج بنجاح على القناة {channel}")

            except Exception as e:
                bot.send_message(user_id, f"⚠️ حدث خطأ أثناء إعلان النتائج: {str(e)}")

        seconds_until_result = (result_time - datetime.now()).total_seconds()
        if seconds_until_result > 0:
            t = threading.Timer(seconds_until_result, post_results)
            t.daemon = True
            t.start()
        else:
            bot.send_message(user_id, "⚠️ وقت إعلان النتائج قد انتهى بالفعل.")

    except Exception as e:
        bot.send_message(user_id, f"⚠️ حدث خطأ أثناء جدولة النتائج: {str(e)}")

# حذف المسابقة
@bot.callback_query_handler(func=lambda call: call.data == "delete_giveaway")
@handle_errors
def delete_giveaway(call):
    user_id = str(call.from_user.id)

    if user_id in bot_data:
        bot_data[user_id]["image"] = None
        bot_data[user_id]["button_text"] = None
        bot_data[user_id]["winners_count"] = None
        bot_data[user_id]["selected_channel"] = None
        bot_data[user_id]["publish_date"] = None
        bot_data[user_id]["result_time"] = None
        bot_data[user_id]["current_operation"] = None
        save_data(bot_data)

    bot.send_message(call.message.chat.id, "❌ تم حذف المسابقة والرجوع إلى القائمة الرئيسية.\n"
                                           "لإنشاء مسابقة جديدة اضغط /start", parse_mode="Markdown")

# قائمة الهدايا
@bot.callback_query_handler(func=lambda call: call.data == "list_giveaways")
@handle_errors
def list_giveaways(call):
    user_id = str(call.from_user.id)
    giveaways = bot_data.get(user_id, {}).get("giveaways", [])

    if not giveaways:
        bot.send_message(call.message.chat.id, "📜 ليس لديك أي هدايا حتى الآن.")
        return

    for idx, giveaway in enumerate(giveaways, 1):
        status_text = giveaway.get("status", "قيد الإنتظار")
        result_time_info = f"⏱ وقت إعلان النتائج: بعد {giveaway['result_time']['text']} من النشر\n" if "result_time" in giveaway else ""
        winners_info = f"🏆 الفائزون: {', '.join(giveaway['winners'])}\n" if giveaway.get("status") == "completed" else ""
        
        bot.send_message(call.message.chat.id, f"🎁 *هدية #{idx}*\n"
                                               f"📅 تاريخ النشر: {giveaway['publish_date']}\n"
                                               f"{result_time_info}"
                                               f"🏆 عدد الفائزين: {giveaway['winners_count']}\n"
                                               f"📡 القنوات المطلوبة: {', '.join(giveaway['channels']) if giveaway['channels'] else 'لا توجد قنوات'}\n"
                                               f"📊 الحالة: {status_text}\n"
                                               f"{winners_info}",
                                               parse_mode="Markdown")

# قنواتي
@bot.callback_query_handler(func=lambda call: call.data == "my_channels")
@handle_errors
def my_channels(call):
    user_id = str(call.from_user.id)
    channels = bot_data.get(user_id, {}).get("channels", [])

    if not channels:
        bot.send_message(call.message.chat.id, "📡 ليس لديك أي قنوات مضافة بعد.")
        return

    markup = InlineKeyboardMarkup()
    for channel in channels:
        markup.add(InlineKeyboardButton(f"❌ حذف {channel}", callback_data=f"delete_channel_{channel}"))

    markup.add(InlineKeyboardButton("⬅️ الرجوع إلى القائمة الرئيسية", callback_data="main_menu"))

    bot.send_message(call.message.chat.id, "📡 **قنواتك:**\n" + "\n".join(channels), parse_mode="Markdown", reply_markup=markup)

# حذف القناة
@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_channel_"))
@handle_errors
def delete_channel(call):
    user_id = str(call.from_user.id)
    channel_to_delete = call.data.replace("delete_channel_", "")

    if channel_to_delete in bot_data[user_id]["channels"]:
        bot_data[user_id]["channels"].remove(channel_to_delete)
        save_data(bot_data)
        bot.send_message(call.message.chat.id, f"✅ تم حذف القناة: {channel_to_delete}")
    else:
        bot.send_message(call.message.chat.id, "⚠️ القناة غير موجودة في القائمة.")

    my_channels(call)

# مسح جميع البيانات
@bot.message_handler(commands=['clear'])
@handle_errors
def clear_data(message):
    user_id = str(message.from_user.id)
    if user_id in bot_data:
        bot_data[user_id] = {
            "username": message.from_user.username or f"User_{user_id}",
            "image": None,
            "button_text": None,
            "channels": [],
            "winners_count": None,
            "selected_channel": None,
            "publish_date": None,
            "result_time": None,
            "giveaways": [],
            "current_operation": None
        }
        save_data(bot_data)
        bot.send_message(message.chat.id, "✅ تم مسح جميع البيانات بنجاح!")
    else:
        bot.send_message(message.chat.id, "⚠️ لا توجد بيانات لمسحها.")

# الرجوع إلى القائمة الرئيسية
@bot.callback_query_handler(func=lambda call: call.data == "main_menu")
@handle_errors
def return_to_main_menu(call):
    start(call.message)

# التحقق من المسابقات المعلقة
@handle_errors
def check_pending_giveaways():
    current_time = datetime.now()
    
    for user_id, user_data in bot_data.items():
        if "giveaways" in user_data:
            for idx, giveaway in enumerate(user_data["giveaways"]):
                if giveaway.get("status") == "pending":
                    publish_date = datetime.strptime(giveaway["publish_date"], "%Y-%m-%d %H:%M")
                    result_time = publish_date + timedelta(minutes=giveaway["result_time"]["value"])
                    
                    if current_time >= result_time:
                        schedule_giveaway_result(user_id, idx)
                    elif current_time >= publish_date:
                        publish_giveaway(user_id, idx)

# بدء تشغيل البوت
threading.Thread(target=check_pending_giveaways, daemon=True).start()
print("🤖 البوت يعمل الآن...")
server()
bot.infinity_polling(none_stop=True)
