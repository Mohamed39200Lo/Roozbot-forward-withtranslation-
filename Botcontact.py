import telebot
from telebot import types
from telebot.types import ReactionTypeEmoji
import logging
import time
from app import server
#from app import server

# استبدل 'YOUR_BOT_TOKEN' ب token البوت الخاص بك
bot = telebot.TeleBot('7674278704:AAFJu7kgwuRpG1YKnWdCYfO9J7Na8MXrblc')

# إعداد logging لتسجيل الأخطاء
logging.basicConfig(filename='bot_errors.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# قاموس لتتبع الحالة الحالية لكل مستخدم
user_state = {}

# قاموس لتخزين الرسائل المتعددة لكل مستخدم
user_messages = {}

# تعريف الأزرار الإنلاين
def create_inline_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton('اريد معرفة طريقة الطلب 🌐', callback_data='how_to_order')
    btn2 = types.InlineKeyboardButton('البحث عن منتج جديد', callback_data='new_order')
    btn3 = types.InlineKeyboardButton('تحديث رابط منتج مغلق 🖇', callback_data='update_closed_link')
    btn4 = types.InlineKeyboardButton('استفسار عن طلب سابق 👨‍💻', callback_data='previous_order_inquiry')
    btn5 = types.InlineKeyboardButton('لدي مشكلة في طلبي بعد الاستلام اريد ارجاعه 📫', callback_data='return_request')
    markup.add(btn1, btn2, btn3, btn4, btn5)
    return markup

# بدء البوت
@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        bot.send_message(message.chat.id, "مرحبًا! كيف يمكنني مساعدتك؟ ", reply_markup=create_inline_keyboard())
    except Exception as e:
        logging.error(f"Error in send_welcome: {e}")

# معالجة الأزرار الإنلاين
@bot.callback_query_handler(func=lambda call: call.data not in ['hoo'])
def handle_inline_buttons(call):
    chat_id = call.message.chat.id

    try:
        # إلغاء أي `next_step_handler` سابق لمنع التكرار
        bot.clear_step_handler(call.message)

        # تحديث حالة المستخدم ومسح أي بيانات سابقة
        user_state[chat_id] = call.data
        user_messages[chat_id] = []

        # إرسال التعليمات المناسبة لكل زر
        instructions = {
            'how_to_order': "طريقة الطلب من علي اكسبريس:\nhttps://youtube.com/shorts/oMJW2vyFtiQ?feature=share\n\n"
                            "طريقة الطلب من DHGATE:\nhttps://youtube.com/shorts/fadcN_wiyGY?feature=share",
            'new_order': "يرجى إرسال رابط المنتج أو صورة المنتج.",
            'update_closed_link': "شكرا على تواصلكم معنا ❤️\n\nيرجى إرسال رابط او صورة المنتج المغلق.",
            'previous_order_inquiry': "شكرا على تواصلكم معنا ❤️\n\nيرجى ارسال رقم الطلب.",
            'return_request': "يرجى كتابة تفاصيل المشكلة وسنقوم بالرد عليك قريبًا."
        }

        bot.send_message(chat_id, instructions[call.data])

        # تسجيل `next_step_handler` فقط للخيارات التي تحتاج إدخال إضافي
        if call.data in ['new_order', 'update_closed_link', 'previous_order_inquiry', 'return_request']:
            bot.register_next_step_handler(call.message, handle_multi_step_message)

    except Exception as e:
        logging.error(f"Error in handle_inline_buttons: {e}")

def handle_multi_step_message(message):
    chat_id = message.chat.id

    try:
        if message.text == '/done':
            forward_to_customer_service(message, user_state.get(chat_id))
            user_messages[chat_id] = []  # إعادة تهيئة قائمة الرسائل
            bot.send_message(chat_id, "تم إرسال طلبك إلى خدمة العملاء.")
        else:
            user_messages[chat_id].append(message)
            bot.send_message(chat_id, """ لخدمتك بشكل اسرع نرجو ارسال المزيد من التفاصيل لطلباتك 😘

أو الضغط على /done  👉  هنا 
 لإتمام الإرسال لخدمة العملاء

📍ملاحظة : عدم الضغط على /done لن تصلنا رسائلك 😔""")
            bot.register_next_step_handler(message, handle_multi_step_message)
    except Exception as e:
        logging.error(f"Error in handle_multi_step_message: {e}")

# تحويل الرسالة إلى خدمة العملاء
def forward_to_customer_service(message, subject):
    try:
        customer_service_chat_id = "-1002427446386"
        username = message.from_user.username if message.from_user.username else message.from_user.first_name
        subject_translations = {
            "new_order": "طلب منتج جديد",
            "update_closed_link": "تحديث رابط منتج مغلق",
            "previous_order_inquiry": "استفسار عن طلب سابق",
            "return_request": "مشكلة في طلبي بعد الاستلام"
        }
        english_subject = subject_translations.get(subject, subject)

        if user_messages[message.chat.id]:
            first_message = user_messages[message.chat.id][0]
            bot.send_message(
                customer_service_chat_id,
                f"📩 رسالة جديدة / New Message\n"
                f"📌 الموضوع / Subject: {subject} / {english_subject}\n"
                f"🆔 chat_id: `{message.chat.id}`\n"
                f"📄 message_id: `{first_message.message_id}`\n"
                f"👤 username: @{username}"
            )

            for msg in user_messages[message.chat.id]:
                bot.forward_message(customer_service_chat_id, message.chat.id, msg.message_id)

    except Exception as e:
        logging.error(f"Error in forward_to_customer_service: {e}")
        
# تحويل الرسالة إلى خدمة العملاء
subject_translations = {
    "new_order": "طلب منتج جديد",
    "update_closed_link": "تحديث رابط منتج مغلق",
    "previous_order_inquiry": "استفسار عن طلب سابق",
    "return_request": "مشكلة في طلبي بعد الاستلام",
}

def create_reply_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn = types.InlineKeyboardButton('الرد على خدمة العملاء', callback_data='hoo')
    markup.add(btn)
    return markup



        
@bot.message_handler(content_types=['text', 'photo', 'video', 'document', 'audio', 'voice', 'sticker'])
def handle_customer_service_reply(message):
    try:
        if message.reply_to_message:
            print("هناك رد على الرسالة")  # تأكيد استقبال الردود
            
            original_message = message.reply_to_message

            # التأكد من أن الرسالة الأصلية تحتوي على chat_id و message_id
            if original_message.text and "chat_id:" in original_message.text and "message_id:" in original_message.text:
                try:
                    # استخراج chat_id و message_id من الرسالة الأصلية
                    chat_id = int(original_message.text.split("chat_id: `")[1].split("`")[0].strip())
                    message_id = int(original_message.text.split("message_id: `")[1].split("`")[0].strip())
                except (ValueError, IndexError) as e:
                    logging.error(f"Error extracting chat_id or message_id: {e}")
                    bot.send_message(message.chat.id, "تعذر استخراج chat_id أو message_id من الرسالة الأصلية.")
                    return

                # إرسال الرد إلى المستخدم الأصلي كرد على الرسالة الأصلية
                if message.text:
                    bot.send_message(chat_id, f"رد من خدمة العملاء:\n{message.text}", reply_to_message_id=message_id, reply_markup=create_reply_keyboard())
                elif message.photo:
                    bot.send_photo(chat_id, message.photo[-1].file_id, caption=message.caption, reply_to_message_id=message_id, reply_markup=create_reply_keyboard())
                elif message.video:
                    bot.send_video(chat_id, message.video.file_id, caption=message.caption, reply_to_message_id=message_id, reply_markup=create_reply_keyboard())
                elif message.document:
                    bot.send_document(chat_id, message.document.file_id, caption=message.caption, reply_to_message_id=message_id, reply_markup=create_reply_keyboard())
                elif message.audio:
                    bot.send_audio(chat_id, message.audio.file_id, caption=message.caption, reply_to_message_id=message_id, reply_markup=create_reply_keyboard())
                elif message.voice:
                    bot.send_voice(chat_id, message.voice.file_id, reply_to_message_id=message_id, reply_markup=create_reply_keyboard())
                elif message.sticker:
                    bot.send_sticker(chat_id, message.sticker.file_id, reply_to_message_id=message_id, reply_markup=create_reply_keyboard())
                else:
                    print("تم استقبال رد لكن نوع المرفق غير مدعوم")
                    bot.send_message(message.chat.id, "  نوع المرفق غير مدعوم.")
                
                # إضافة لايك على رسالة خدمة العملاء بعد نجاح التوجيه
                try:
                    bot.set_message_reaction(message.chat.id, message.id, [ReactionTypeEmoji('👍')], is_big=False)
                    print("تم إضافة لايك على رسالة خدمة العملاء.")
                except Exception as reaction_error:
                    logging.error(f"Error setting reaction: {reaction_error}")
            else:
                bot.send_message(message.chat.id, "الرجاء الرد على رسالة تحتوي على chat_id و message_id.")
        else:
            print("لم يتم التعرف على reply_to_message")  # تأكيد أن البوت لم يتعرف على الرد
    except Exception as e:
        logging.error(f"Error in handle_customer_service_reply: {e}")   
             
@bot.callback_query_handler(func=lambda call: call.data == 'hoo')
def handle_reply_to_customer_service(call):
    try:
        print(1)
        chat_id = call.message.chat.id
        bot.send_message(chat_id, "يرجى إرسال ردك على خدمة العملاء.")
        bot.register_next_step_handler(call.message, forward_user_reply_to_customer_service)
    except Exception as e:
        logging.error(f"Error in handle_reply_to_customer_service: {e}")        


def forward_user_reply_to_customer_service(message):
    try:
        # استبدل 'CUSTOMER_SERVICE_CHAT_ID' بمعرف الدردشة الخاصة بخدمة العملاء
        customer_service_chat_id = "-1002427446386"
        
        # الحصول على اسم المستخدم (username) أو الاسم الأول إذا لم يكن username متاحًا
        username = message.from_user.username if message.from_user.username else message.from_user.first_name
        
        # إرسال الرسالة إلى خدمة العملاء
        bot.send_message(
            customer_service_chat_id,
            f"📩 رد من المستخدم / User Reply\n"
            f"🆔 chat_id: `{message.chat.id}`\n"
            f"📄 message_id: `{message.message_id}`\n"
            f"👤 username: @{username}"
        )
        
        # تحويل الرسالة الأصلية
        bot.forward_message(customer_service_chat_id, message.chat.id, message.message_id)
        
        # إعلام المستخدم بأن ردهم قد تم إرساله
        #bot.send_message(message.chat.id, "تم إرسال ردك إلى خدمة العملاء.")
        bot.send_message(message.chat.id, " تم إرسال ردك إلى خدمة العملاء. اضغط على الزر لإرسال رد آخر",reply_markup=create_reply_keyboard())
        
    except Exception as e:
        logging.error(f"Error in forward_user_reply_to_customer_service: {e}")
        
server()        
# تشغيل البوت مع إعادة التشغيل التلقائي في حالة التوقف
while True:
    try:
        bot.polling(none_stop=True)  # none_stop=True يمنع البوت من التوقف عند حدوث أخطاء بسيطة
    except Exception as e:
        logging.error(f"Bot stopped due to an error: {e}")
        time.sleep(5)  # انتظر 5 ثواني قبل إعادة التشغيل
        print("إعادة تشغيل البوت...")
