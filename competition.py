
import telebot
import json
import os
import re
import random
import threading
from datetime import datetime, timedelta
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from app import server

# استبدل بـ token البوت الخاص بك
TOKEN = "7710195977:AAEiamn8qPONy90CxvmS29iWXv8f1rFUBEU"
bot = telebot.TeleBot(TOKEN)

# ملف لحفظ بيانات البوت
DATA_FILE = "bot_daty6ua.json"

# تحميل البيانات من الملف
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# حفظ البيانات في الملف
def save_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"⚠️ حدث خطأ أثناء حفظ البيانات: {str(e)}")

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
            "giveaways": []
        }
    else:
        bot_data[user_id]["username"] = username

    return bot_data[user_id]

# أمر البدء
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    username = message.from_user.username or f"User_{user_id}"
    
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
def create_giveaway(call):
    bot.send_message(call.message.chat.id, "🎁 *إنشاء هدية*\n\n"
                                       "**ارسل رسالة نصية للسحب، يمكنك أيضًا إرسال صورة أو مقطع فيديو أو صورة GIF مع النص.**\n\n"
                                       "*يمكنك استخدام ملف وسائط واحد فقط.*\n\n"
                                       "**بوت إجراء المسابقات مجاني تمامًا وشفاف وبدون إعلانات، وسيسعد إذا قمت بالإشارة إلى رابط له في منشور المسابقة. شكرًا لك @RooGiftsBot**",                     
                 parse_mode="Markdown")
    bot.register_next_step_handler(call.message, save_giveaway_image)

# حفظ صورة الهدية
def save_giveaway_image(message):
    user_id = str(message.from_user.id)

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
def save_button_text(message):
    user_id = str(message.from_user.id)
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
def add_channels(message):
    user_id = str(message.from_user.id)
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
def add_another_channel(call):
    bot.send_message(call.message.chat.id, "🔹 *يرجى إرسال القناة الإضافية بنفس التنسيق:* @channelname", parse_mode="Markdown")
    bot.register_next_step_handler(call.message, add_channels)

# الاستمرار إلى اختيار الفائزين
@bot.callback_query_handler(func=lambda call: call.data == "continue_to_winners")
def continue_to_winners(call):
    bot.send_message(call.message.chat.id, "🔹 *كم عدد الفائزين الذين يجب على الروبوت اختيارهم؟*", parse_mode="Markdown")
    bot.register_next_step_handler(call.message, set_winners_count)

# تعيين عدد الفائزين
def set_winners_count(message):
    user_id = str(message.from_user.id)

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
def set_publish_date(message):
    user_id = str(message.from_user.id)
    date_pattern = r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$"

    if not re.match(date_pattern, message.text):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("⬅️ الرجوع إلى القائمة الرئيسية", callback_data="main_menu"))
        
        bot.send_message(message.chat.id, "⚠️ التنسيق خطأ! الرجاء إرسال التاريخ بتنسيق YYYY-MM-DD HH:MM\n\n"
                                         "اضغط على الزر أدناه للعودة إلى القائمة الرئيسية:", reply_markup=markup)
        bot.register_next_step_handler(message, set_publish_date)
        return

    bot_data[user_id]["publish_date"] = message.text
    save_data(bot_data)
    
    bot.send_message(message.chat.id, "✅ تم حفظ تاريخ النشر!")

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("2 دقائق", callback_data="result_time_2min"))
    markup.add(InlineKeyboardButton("10 دقائق", callback_data="result_time_10min"))
    markup.add(InlineKeyboardButton("ساعة", callback_data="result_time_1hour"))
    markup.add(InlineKeyboardButton("يوم", callback_data="result_time_1day"))

    bot.send_message(message.chat.id, "🔹 *ما التوقيت الذي تريده لإعلان نتيجة السحب؟*", 
                     parse_mode="Markdown", reply_markup=markup)

# تعيين وقت النتيجة
@bot.callback_query_handler(func=lambda call: call.data.startswith("result_time_"))
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
        "participants": []  # قائمة المشاركين في المسابقة
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
def join_giveaway(call):
    # استخراج معرف المسابقة من بيانات الـ callback
    giveaway_idx = int(call.data.replace("join_giveaway_", ""))
    
    # الحصول على بيانات المستخدم الذي ضغط على الزر
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

    # التحقق من أن المستخدم مشترك في القنوات المطلوبة
    required_channels = giveaway["channels"]
    user_is_subscribed = True

    for channel in required_channels:
        try:
            # التحقق من اشتراك المستخدم في القناة
            chat_member = bot.get_chat_member(channel, call.from_user.id)
            if chat_member.status not in ["member", "administrator", "creator"]:
                user_is_subscribed = False
                break
        except Exception as e:
            # إذا حدث خطأ (مثل عدم وجود البوت في القناة)
            user_is_subscribed = False
            break

    if not user_is_subscribed:
        bot.answer_callback_query(call.id, "⚠️ يجب أن تكون مشتركًا في جميع القنوات المطلوبة للمشاركة في المسابقة.")
        return

    # إضافة المستخدم إلى قائمة المشاركين إذا لم يكن مشاركًا بالفعل
    if user_id not in giveaway["participants"]:
        giveaway["participants"].append({
            "user_id": user_id,
            "username": username
        })
        save_data(bot_data)
        bot.answer_callback_query(call.id, "✅ تم الانضمام إلى المسابقة بنجاح!")
    else:
        bot.answer_callback_query(call.id, "⚠️ أنت بالفعل مشارك في هذه المسابقة.")
   
        
             
    # التحقق من أن المستخدم مشترك في القنوات المطلوبة
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

    # إضافة المستخدم إلى قائمة المشاركين إذا لم يكن مشاركًا بالفعل
    if user_id not in giveaway["participants"]:
        giveaway["participants"].append(user_id)
        save_data(bot_data)
        bot.answer_callback_query(call.id, "✅ تم الانضمام إلى المسابقة بنجاح!")
    else:
        bot.answer_callback_query(call.id, "⚠️ أنت بالفعل مشارك في هذه المسابقة.")

# جدولة إعلان النتائج
def schedule_giveaway_result(user_id, giveaway_idx):
    try:
        # الحصول على بيانات المسابقة
        giveaway = bot_data[user_id]["giveaways"][giveaway_idx]
        channel = giveaway["selected_channel"]

        # حساب وقت إعلان النتائج
        publish_date = datetime.strptime(giveaway["publish_date"], "%Y-%m-%d %H:%M")
        result_minutes = giveaway["result_time"]["value"]
        result_time = publish_date + timedelta(minutes=result_minutes)

        print(f"⏱ سيتم إعلان النتائج في: {result_time}")

        # دالة لإعلان النتائج
        def post_results():
            try:
                # التحقق من وجود مشاركين
                if not giveaway["participants"]:
                    bot.send_message(user_id, "⚠️ لا يوجد مشاركين في المسابقة لاختيار الفائزين.")
                    return

                # إزالة التكرارات من قائمة المشاركين
                unique_participants = []
                seen_user_ids = set()

                for participant in giveaway["participants"]:
                    # إذا كان العنصر نصيًا (user_id فقط)
                    if isinstance(participant, str):
                        user_id_winner = participant
                        if user_id_winner not in seen_user_ids:
                            seen_user_ids.add(user_id_winner)
                            unique_participants.append({"user_id": user_id_winner, "username": None})
                    
                    # إذا كان العنصر قاموسًا (يحتوي على user_id و username)
                    elif isinstance(participant, dict):
                        user_id_winner = participant["user_id"]
                        if user_id_winner not in seen_user_ids:
                            seen_user_ids.add(user_id_winner)
                            unique_participants.append(participant)
                    
                    else:
                        print(f"⚠️ تنسيق غير معروف للمشارك: {participant}")
                        continue

                # اختيار الفائزين
                winners_count = min(giveaway["winners_count"], len(unique_participants))
                winners = random.sample(unique_participants, winners_count)

                # إعداد رسالة الفائزين
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
                        print(f"⚠️ خطأ في الحصول على بيانات الفائز: {winner} - {str(e)}")
                        continue

                if not valid_winners:
                    bot.send_message(user_id, "⚠️ لا يمكن العثور على أي فائزين صالحين.")
                    return

                winners_message += ", ".join(valid_winners) + "\n\nتهانينا للفائزين! 🎊"

                # تحديث حالة المسابقة
                giveaway["status"] = "completed"
                giveaway["winners"] = valid_winners
                save_data(bot_data)

                # إرسال رسالة النتائج إلى القناة
                bot.send_message(channel, winners_message, parse_mode="Markdown")
                bot.send_message(user_id, f"✅ تم إعلان النتائج بنجاح على القناة {channel}")

            except Exception as e:
                bot.send_message(user_id, f"⚠️ حدث خطأ أثناء إعلان النتائج: {str(e)}")

        # حساب الوقت المتبقي حتى إعلان النتائج
        seconds_until_result = (result_time - datetime.now()).total_seconds()
        if seconds_until_result > 0:
            print(f"⏳ الوقت المتبقي لإعلان النتائج: {seconds_until_result} ثانية")
            t = threading.Timer(seconds_until_result, post_results)
            t.daemon = True
            t.start()
        else:
            bot.send_message(user_id, "⚠️ وقت إعلان النتائج قد انتهى بالفعل.")

    except Exception as e:
        bot.send_message(user_id, f"⚠️ حدث خطأ أثناء جدولة النتائج: {str(e)}")

# حذف المسابقة
@bot.callback_query_handler(func=lambda call: call.data == "delete_giveaway")
def delete_giveaway(call):
    user_id = str(call.from_user.id)

    if user_id in bot_data:
        # حذف المسابقة الحالية
        bot_data[user_id]["image"] = None
        bot_data[user_id]["button_text"] = None
        bot_data[user_id]["winners_count"] = None
        bot_data[user_id]["selected_channel"] = None
        bot_data[user_id]["publish_date"] = None
        bot_data[user_id]["result_time"] = None
        save_data(bot_data)

    bot.send_message(call.message.chat.id, "❌ تم حذف المسابقة والرجوع إلى القائمة الرئيسية.\n"
                                           "لإنشاء مسابقة جديدة اضغط /start", parse_mode="Markdown")

# قائمة الهدايا
@bot.callback_query_handler(func=lambda call: call.data == "list_giveaways")
def list_giveaways(call):
    user_id = str(call.from_user.id)
    giveaways = bot_data.get(user_id, {}).get("giveaways", [])

    if not giveaways:
        bot.send_message(call.message.chat.id, "📜 ليس لديك أي هدايا حتى الآن.")
        return

    for idx, giveaway in enumerate(giveaways, 1):
        status_text = "قيد الإنتظار"
        if "status" in giveaway:
            if giveaway["status"] == "active":
                status_text = "نشطة"
            elif giveaway["status"] == "completed":
                status_text = "مكتملة"
            elif giveaway["status"] == "cancelled":
                status_text = "ملغية"
        
        result_time_info = ""
        if "result_datetime" in giveaway:
            result_time_info = f"⏱ وقت إعلان النتائج: {giveaway['result_datetime']}\n"
        elif "result_time" in giveaway:
            result_time_info = f"⏱ وقت إعلان النتائج: بعد {giveaway['result_time']['text']} من النشر\n"
        
        winners_info = ""
        if "winners" in giveaway and giveaway.get("status") == "completed":
            winners_info = f"🏆 الفائزون: {', '.join(giveaway['winners'])}\n"
        
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

# الرجوع إلى القائمة الرئيسية
@bot.callback_query_handler(func=lambda call: call.data == "main_menu")
def return_to_main_menu(call):
    start(call.message)

# التحقق من المسابقات المعلقة
def check_pending_giveaways():
    current_time = datetime.now()
    
    for user_id, user_data in bot_data.items():
        if "giveaways" in user_data:
            for idx, giveaway in enumerate(user_data["giveaways"]):
                if giveaway.get("status") == "pending":
                    publish_date = datetime.strptime(giveaway["publish_date"], "%Y-%m-%d %H:%M")
                    result_time = publish_date + timedelta(minutes=giveaway["result_time"]["value"])
                    
                    if current_time >= result_time:
                        # إذا انتهى وقت النتائج، يتم إعلان النتائج
                        schedule_giveaway_result(user_id, idx)
                    elif current_time >= publish_date:
                        # إذا لم يتم نشر المسابقة بعد، يتم جدولة النشر
                        publish_giveaway(user_id, idx)

# بدء تشغيل البوت مع التحقق من المسابقات المعلقة
threading.Thread(target=check_pending_giveaways, daemon=True).start()
print("🤖 البوت يعمل الآن...")
server()
bot.infinity_polling(none_stop=True)
