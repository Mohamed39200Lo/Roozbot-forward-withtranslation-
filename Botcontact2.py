
import telebot
from telebot import types
from app import server
import logging
import time
from telebot.types import ReactionTypeEmoji

# استبدل 'YOUR_BOT_TOKEN' ب token البوت الخاص بك
bot = telebot.TeleBot('7831660630:AAHNYrla0bbvhXwSOOwbo-8ivEe-SlQYfg0')

# إعداد logging لتسجيل الأخطاء
logging.basicConfig(filename='bot_errors.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# قاموس لتتبع الحالة الحالية لكل مستخدم
user_state = {}

# تعريف الأزرار الإنلاين
def create_inline_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton('اريد معرفة طريقة الطلب 🌐', callback_data='how_to_order')
    btn2 = types.InlineKeyboardButton('طلب منتج جديد', callback_data='new_order')
    btn3 = types.InlineKeyboardButton('تحديث رابط منتج مغلق 🖇', callback_data='update_closed_link')
    btn4 = types.InlineKeyboardButton('استفسار عن طلب سابق 👨‍💻', callback_data='previous_order_inquiry')
    btn5 = types.InlineKeyboardButton('لدي مشكلة في طلبي بعد الاستلام اريد ارجاعه 📫', callback_data='return_request')
    markup.add(btn1, btn2, btn3, btn4, btn5)
    return markup

# بدء البوت
@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        bot.send_message(message.chat.id, "مرحبًا! كيف يمكنني مساعدتك؟ Rooz", reply_markup=create_inline_keyboard())
    except Exception as e:
        logging.error(f"Error in send_welcome: {e}")

# معالجة الأزرار الإنلاين
@bot.callback_query_handler(func=lambda call: True)
def handle_inline_buttons(call):
    chat_id = call.message.chat.id

    try:
        # تحديث الحالة الحالية للمستخدم
        user_state[chat_id] = call.data

        if call.data == 'how_to_order':
            response = (
                """
                طريقة الطلب من علي اكسبريس

https://youtube.com/shorts/oMJW2vyFtiQ?feature=share


طريقة الطلب من DHGATE 

https://youtube.com/shorts/fadcN_wiyGY?feature=share
"""
            )
            bot.send_message(chat_id, response)

        elif call.data == 'new_order':
            bot.send_message(chat_id, "يرجى إرسال رابط المنتج أو صورة المنتج.")
            bot.register_next_step_handler(call.message, handle_product_request)

        elif call.data == 'update_closed_link':
            bot.send_message(chat_id, """شكرا على تواصلكم معنا ❤️
يرجى إرسال رابط المنتج المغلق """)
            bot.register_next_step_handler(call.message, handle_closed_link)

        elif call.data == 'previous_order_inquiry':
            bot.send_message(chat_id, """شكرا على تواصلكم معنا ❤️
يرجى ارسال رقم الطلب""")
            bot.register_next_step_handler(call.message, handle_inquiry)

        elif call.data == 'return_request':
            bot.send_message(chat_id, "يرجى كتابة تفاصيل المشكلة وسنقوم بالرد عليك قريبًا.")
            bot.register_next_step_handler(call.message, handle_return_request)
    except Exception as e:
        logging.error(f"Error in handle_inline_buttons: {e}")

# معالجة طلب منتج جديد
def handle_product_request(message):
    try:
        if user_state.get(message.chat.id) == 'new_order':
            bot.send_message(message.chat.id, "تم استلام طلبك. سنقوم بالتواصل معك قريبًا.")
            forward_to_customer_service(message, "طلب منتج جديد")
    except Exception as e:
        logging.error(f"Error in handle_product_request: {e}")

# معالجة تحديث رابط منتج مغلق
def handle_closed_link(message):
    try:
        if user_state.get(message.chat.id) == 'update_closed_link':
            bot.send_message(message.chat.id, "تم استلام رابط المنتج المغلق. سنقوم بالتواصل معك قريبًا.")
            forward_to_customer_service(message, "تحديث رابط منتج مغلق")
    except Exception as e:
        logging.error(f"Error in handle_closed_link: {e}")

# معالجة استفسار عن طلب سابق
def handle_inquiry(message):
    try:
        if user_state.get(message.chat.id) == 'previous_order_inquiry':
            bot.send_message(message.chat.id, "تم استلام استفسارك. سنقوم بالرد عليك قريبًا.")
            forward_to_customer_service(message, "استفسار عن طلب سابق")
    except Exception as e:
        logging.error(f"Error in handle_inquiry: {e}")

# معالجة طلب إرجاع منتج
def handle_return_request(message):
    try:
        if user_state.get(message.chat.id) == 'return_request':
            bot.send_message(message.chat.id, "تم استلام تفاصيل مشكلتك. سنقوم بالتواصل معك قريبًا.")
            forward_to_customer_service(message, "مشكلة في طلبي بعد الاستلام")
    except Exception as e:
        logging.error(f"Error in handle_return_request: {e}")


# تحويل الرسالة إلى خدمة العملاء
# قاموس لترجمة المواضيع إلى الإنجليزية
subject_translations = {
    "طلب منتج جديد": "New product order",
    "تحديث رابط منتج مغلق": "Update closed product link",
    "استفسار عن طلب سابق": "Inquiry about a previous order",
    "مشكلة في طلبي بعد الاستلام": "Issue with my order after delivery",
}

# تحويل الرسالة إلى خدمة العملاء
def forward_to_customer_service(message, subject):
    try:
        # استبدل 'CUSTOMER_SERVICE_CHAT_ID' بمعرف الدردشة الخاصة بخدمة العملاء
        customer_service_chat_id = "-1002448434150"
        
        # الحصول على اسم المستخدم (username) أو الاسم الأول إذا لم يكن username متاحًا
        username = message.from_user.username if message.from_user.username else message.from_user.first_name
        
        # الحصول على الترجمة الإنجليزية للموضوع من القاموس
        english_subject = subject_translations.get(subject, subject)  
        
        bot.send_message(
            customer_service_chat_id,
            f"📩 رسالة جديدة / New Message\n"
            f"📌 الموضوع / Subject: {subject} / {english_subject}\n"
            f"🆔 chat_id: `{message.chat.id}`\n"
            f"📄 message_id: `{message.message_id}`\n"
            f"👤 username: @{username}"
        )
        
        # تحويل الرسالة الأصلية
        bot.forward_message(customer_service_chat_id, message.chat.id, message.message_id)
    except Exception as e:
        logging.error(f"Error in forward_to_customer_service: {e}")

# معالجة ردود خدمة العملاء
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
                    bot.send_message(chat_id, f"رد من خدمة العملاء:\n{message.text}", reply_to_message_id=message_id)
                elif message.photo:
                    bot.send_photo(chat_id, message.photo[-1].file_id, caption=message.caption, reply_to_message_id=message_id)
                elif message.video:
                    bot.send_video(chat_id, message.video.file_id, caption=message.caption, reply_to_message_id=message_id)
                elif message.document:
                    bot.send_document(chat_id, message.document.file_id, caption=message.caption, reply_to_message_id=message_id)
                elif message.audio:
                    bot.send_audio(chat_id, message.audio.file_id, caption=message.caption, reply_to_message_id=message_id)
                elif message.voice:
                    bot.send_voice(chat_id, message.voice.file_id, reply_to_message_id=message_id)
                elif message.sticker:
                    bot.send_sticker(chat_id, message.sticker.file_id, reply_to_message_id=message_id)
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

server()

# تشغيل البوت مع إعادة التشغيل التلقائي في حالة التوقف
while True:
    try:
        bot.polling(none_stop=True)  # none_stop=True يمنع البوت من التوقف عند حدوث أخطاء بسيطة
    except Exception as e:
        logging.error(f"Bot stopped due to an error: {e}")
        time.sleep(5)  # انتظر 5 ثواني قبل إعادة التشغيل
        print("إعادة تشغيل البوت...")
