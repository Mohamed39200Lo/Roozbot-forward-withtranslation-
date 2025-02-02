import asyncio
import os
import time
import multiprocessing
from telethon import TelegramClient
from bot1 import *
from bot2 import *
import sys
import subprocess
from telethon import TelegramClient, errors
from app import server
import gunicorn
from Botcontact import run_bot_contact
# التوكن الخاص بالبوت الأول
bot_token = "6933260431:AAG59xJfPUqaDZzS7S6uLk27fEtRAGH2mPg"


	
@app2.on_message(filters.command("reload"))
async def reload_bots(_: Client, message: Message):
    print(77)
    await message.reply("جاري إعادة تشغيل البرنامج...")
    os.execl(sys.executable, sys.executable, *sys.argv)

def restart_program():
    os.execl(sys.executable, sys.executable, *sys.argv)
Tests=0    
async def run_bot1():
    global Tests
    try:
        # بدء البوت باستخدام التوكن مباشرة
        await app1.start(bot_token=bot_token)
        sent_alert = False  # متغير لتتبع ما إذا تم إرسال التنبيه بالفعل أم لا
        while True:
            try:
                # التحقق من الجلسة
                me = await app1.get_me()
                print(f"Bot 1 is running as {me.username}")
                await asyncio.sleep(30)
            except errors.AuthKeyError:  # التعامل مع مشاكل مفتاح المصادقة
                if not sent_alert:  # إذا لم يتم إرسال التنبيه بعد
                    print("Bot 1 session has an authentication key error. Sending alert to Bot 2.")
                    await app2.send_message(1596661941, "هناك مشكلة في جلسة تليجرام. جرب التسجيل مرة أخرى وأعد تشغيل البوت.")
                    sent_alert = True  # قم بتعيين المتغير إلى True بعد إرسال التنبيه
            except Exception as e:
                await app2.send_message(1596661941, f"حدث خطأ أثناء عمل البوت: {str(e)}")
                Tests += 1
                if Tests >= 3:
                    Tests = 0
                    restart_program()
                    time.sleep(350)
                time.sleep(45)
                print(f"An error occurred in bot1: {e}")
    except Exception as e:
        print(f"An error occurred in bot1: {e}")
        pass

async def run_bot2():
    session_file1 = "SessionsExcutor.session"  # 
    session_file2 = "path_to_bot2_session_file_2"  # 
    try:
        if app1.is_connected():
            print(55)
            await app2.stop()
        await app2.start()
        while True:
            await asyncio.sleep(50)
    except AuthKeyDuplicated:
        print("Bot 2 session is duplicated. Deleting session files and restarting.")
        time.sleep(20)

        if os.path.exists(session_file1):
            os.remove(session_file1)
        if os.path.exists(session_file2):
            os.remove(session_file2)
        restart_program()
    except Exception as e:
        print(f"An error occurred in bot2: {e}")
        pass

# تشغيل البوتين في وضع دائم
def main():
    server()

    loop = asyncio.get_event_loop()
	
    # تشغيل بوت الأول
    task1 = asyncio.ensure_future(run_bot1())
    # تشغيل بوت الثاني
    task2 = asyncio.ensure_future(run_bot2())
    task3 = asyncio.create_task(run_bot_contact()) 

    try:
        loop.run_until_complete(asyncio.gather(task1, task2 ,task3))
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"An error occurred in one of the bots: {e}")
    finally:
        loop.stop()

if __name__ == "__main__":
    main()
