import pyrogram
import asyncio
from pyrogram import Client,filters
from pyrogram.types import InlineKeyboardMarkup,InlineKeyboardButton
from os import environ, remove
from threading import Thread
from json import load
from re import search

from texts import HELP_TEXT
import bypasser
import freewall
from time import time


# bot
with open('config.json', 'r') as f: DATA = load(f)
def getenv(var): return environ.get(var) or DATA.get(var, None)

bot_token = getenv("TOKEN")
api_hash = getenv("HASH") 
api_id = getenv("ID")
fsub_id = getenv('FSUB_ID')
app = Client("my_bot",api_id=api_id, api_hash=api_hash,bot_token=bot_token)  


# handle ineex
def handleIndex(ele,message,msg):
    result = bypasser.scrapeIndex(ele)
    try: app.delete_messages(message.chat.id, msg.id)
    except: pass
    for page in result: app.send_message(message.chat.id, page, reply_to_message_id=message.id, disable_web_page_preview=True)


# loop thread
def loopthread(message,otherss=False):

    urls = []
    if otherss: texts = message.caption
    else: texts = message.text

    if texts in [None,""]: return
    for ele in texts.split():
        if "http://" in ele or "https://" in ele:
            urls.append(ele)
    if len(urls) == 0: return

    if bypasser.ispresent(bypasser.ddl.ddllist,urls[0]):
        msg = app.send_message(message.chat.id, "⚡ __generating...__", reply_to_message_id=message.id)
    elif freewall.pass_paywall(urls[0], check=True):
        msg = app.send_message(message.chat.id, "🕴️ __jumping the wall...__", reply_to_message_id=message.id)
    else:
        if "https://olamovies" in urls[0] or "https://psa.wf/" in urls[0]:
            msg = app.send_message(message.chat.id, "⏳ __this might take some time...__", reply_to_message_id=message.id)
        else:
            msg = app.send_message(message.chat.id, "🔎 __bypassing...__", reply_to_message_id=message.id)

    strt = time()
    links = ""
    temp = None
    for ele in urls:
        if search(r"https?:\/\/(?:[\w.-]+)?\.\w+\/\d+:", ele):
            handleIndex(ele,message,msg)
            return
        elif bypasser.ispresent(bypasser.ddl.ddllist,ele):
            try: temp = bypasser.ddl.direct_link_generator(ele)
            except Exception as e: temp = "**Error**: " + str(e)
        elif freewall.pass_paywall(ele, check=True):
            freefile = freewall.pass_paywall(ele)
            if freefile:
                try: 
                    app.send_document(message.chat.id, freefile, reply_to_message_id=message.id)
                    remove(freefile)
                    app.delete_messages(message.chat.id,[msg.id])
                    return
                except: pass
            else: app.send_message(message.chat.id, "__Failed to Jump", reply_to_message_id=message.id)
        else:    
            try: temp = bypasser.shortners(ele)
            except Exception as e: temp = "**Error**: " + str(e)
        print("bypassed:",temp)
        if temp != None: links = links + temp + "\n"
    end = time()
    print("Took " + "{:.2f}".format(end-strt) + "sec")

    if otherss:
        try:
            app.send_photo(message.chat.id, message.photo.file_id, f'__{links}__', reply_to_message_id=message.id)
            app.delete_messages(message.chat.id,[msg.id])
            return
        except: pass

    try: 
        final = []
        tmp = ""
        for ele in links.split("\n"):
            tmp += ele + "\n"
            if len(tmp) > 4000:
                final.append(tmp)
                tmp = ""
        final.append(tmp)
        app.delete_messages(message.chat.id, msg.id)
        tmsgid = message.id
        for ele in final:
            tmsg = app.send_message(message.chat.id, f'__{ele}__',reply_to_message_id=tmsgid, disable_web_page_preview=True)
            tmsgid = tmsg.id
    except Exception as e:
        app.send_message(message.chat.id, f"__Failed to Bypass : {e}__", reply_to_message_id=message.id)
        

def is_user_member(client, user_id):
    try:
        member = client.get_chat_member(fsub_id, user_id)
        logging.info(f"User {user_id} membership status: {member.status}")
        if member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return True
        else:
            return False
    except Exception as e:
        logging.error(f"Error checking membership status for user {user_id}: {e}")
        return False




# start command
@app.on_message(filters.command(["start"]))
def send_start(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    user_id = message.from_user.id
    is_member = is_user_member(client, user_id)
    if not is_member:
        join_button = InlineKeyboardButton("ᴊᴏɪɴ ❤️🚀", url="https://t.me/movie_time_botonly") #add your force subchannel url
        reply_markup = InlineKeyboardMarkup([[join_button]])
        message.reply_text("😈ʏᴏᴜ ᴍᴜsᴛ ᴊᴏɪɴ ᴍʏ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴜsᴇ ᴍᴇ😈.", reply_markup=reply_markup)
        return 
        
    app.send_message(message.chat.id, f"__👋 Hi **{message.from_user.mention}**, i am Link Bypasser Bot, just send me any supported links and i will you get you results.\nCheckout /help to Read More__",
    reply_markup=InlineKeyboardMarkup([
        [ InlineKeyboardButton("🌐 Source Code", url="https://t.me/+PBumvx-e43I4ZTE1")],
        [ InlineKeyboardButton("MAIN CHANNEL", url="https://t.me/+PBumvx-e43I4ZTE1") ]]), 
        reply_to_message_id=message.id)


# help command
@app.on_message(filters.command(["help"]))
def send_help(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    user_id = message.from_user.id
    is_member = is_user_member(client, user_id)
    if not is_member:
        join_button = InlineKeyboardButton("ᴊᴏɪɴ ❤️🚀", url="https://t.me/movie_time_botonly") #add your force subchannel url
        reply_markup = InlineKeyboardMarkup([[join_button]])
        message.reply_text("😈ʏᴏᴜ ᴍᴜsᴛ ᴊᴏɪɴ ᴍʏ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴜsᴇ ᴍᴇ😈.", reply_markup=reply_markup)
        return 
    app.send_message(message.chat.id, HELP_TEXT, reply_to_message_id=message.id, disable_web_page_preview=True)


# links
@app.on_message(filters.text)
def receive(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    user_id = message.from_user.id
    is_member = is_user_member(client, user_id)
    if not is_member:
        join_button = InlineKeyboardButton("ᴊᴏɪɴ ❤️🚀", url="https://t.me/movie_time_botonly") #add your force subchannel url
        reply_markup = InlineKeyboardMarkup([[join_button]])
        message.reply_text("😈ʏᴏᴜ ᴍᴜsᴛ ᴊᴏɪɴ ᴍʏ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴜsᴇ ᴍᴇ😈.", reply_markup=reply_markup)
        return 
    bypass = Thread(target=lambda:loopthread(message),daemon=True)
    bypass.start()


# doc thread
def docthread(message):
    user_id = message.from_user.id
    is_member = is_user_member(client, user_id)
    if not is_member:
        join_button = InlineKeyboardButton("ᴊᴏɪɴ ❤️🚀", url="https://t.me/movie_time_botonly") #add your force subchannel url
        reply_markup = InlineKeyboardMarkup([[join_button]])
        message.reply_text("😈ʏᴏᴜ ᴍᴜsᴛ ᴊᴏɪɴ ᴍʏ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴜsᴇ ᴍᴇ😈.", reply_markup=reply_markup)
        return 
    msg = app.send_message(message.chat.id, "🔎 __bypassing...__", reply_to_message_id=message.id)
    print("sent DLC file")
    file = app.download_media(message)
    dlccont = open(file,"r").read()
    links = bypasser.getlinks(dlccont)
    app.edit_message_text(message.chat.id, msg.id, f'__{links}__', disable_web_page_preview=True)
    remove(file)


# files
@app.on_message([filters.document,filters.photo,filters.video])
def docfile(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    user_id = message.from_user.id
    is_member = is_user_member(client, user_id)
    if not is_member:
        join_button = InlineKeyboardButton("ᴊᴏɪɴ ❤️🚀", url="https://t.me/movie_time_botonly") #add your force subchannel url
        reply_markup = InlineKeyboardMarkup([[join_button]])
        message.reply_text("😈ʏᴏᴜ ᴍᴜsᴛ ᴊᴏɪɴ ᴍʏ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴜsᴇ ᴍᴇ😈.", reply_markup=reply_markup)
        return 
    
    try:
        if message.document.file_name.endswith("dlc"):
            bypass = Thread(target=lambda:docthread(message),daemon=True)
            bypass.start()
            return
    except: pass

    bypass = Thread(target=lambda:loopthread(message,True),daemon=True)
    bypass.start()


# server loop
print("Bot Starting")
app.run()
