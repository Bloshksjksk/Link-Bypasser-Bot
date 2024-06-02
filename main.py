import pyrogram
from pyrogram import Client,filters
from pyrogram.types import InlineKeyboardMarkup,InlineKeyboardButton
from os import environ, remove
from threading import Thread
from json import load
from re import search

from texts import HELP_TEXT
import bypasser
import freewall
import pymongo
from pymongo import MongoClient
from time import time


# botTRUMBOT
with open('config.json', 'r') as f: DATA = load(f)
def getenv(var): return environ.get(var) or DATA.get(var, None)

bot_token = getenv("TOKEN")
api_hash = getenv("HASH") 
api_id = getenv("ID")
ADMINS= int(getenv("ADMINS"))
CHANNEL_ID = -1001678093514
app = Client("my_bot",api_id=api_id, api_hash=api_hash,bot_token=bot_token)  
mongo_client = pymongo.MongoClient("mongodb+srv://misoc51233:i1ko1lV8fOryGyrv@cluster0.dmus3p9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = mongo_client.my_database
users_collection = db.users


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
        


# start command
@app.on_message(filters.command(["start"]))
def send_start(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    app.send_message(message.chat.id, f"__👋 Hi **{message.from_user.mention}**, i am Link Bypasser Bot, just send me any supported links and i will you get you results.\nCheckout /help to Read More__",
    reply_markup=InlineKeyboardMarkup([
        [ InlineKeyboardButton("🌐 Source Code", url="https://t.me/+PBumvx-e43I4ZTE1")],
        [ InlineKeyboardButton("MAIN CHANNEL", url="https://t.me/+PBumvx-e43I4ZTE1") ]]), 
        reply_to_message_id=message.id)


# help command
@app.on_message(filters.command(["help"]))
def send_help(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    app.send_message(message.chat.id, HELP_TEXT, reply_to_message_id=message.id, disable_web_page_preview=True)

#newfeatuesbyTRUMBOTS
@app.on_message(filters.command("broadcast"))
async def broadcast_command(client, message):
    # Get the message text
    message_text = message.text

    # Check if the user is an admin
    if message.from_user.id not in ADMINS:
        await message.reply("You are not authorized to use this command.")
        return

    # Get all users from the database
    users = list(users_collection.find({}))

    # Send the message to all users
    for user in users:
        try:
            await client.send_message(user["user_id"], message_text)
        except Exception as e:
            print(e)


@app.on_message(filters.command("total_users"))
async def total_users_command(client, message):
    # Get the total number of users from the database
    total_users = users_collection.count_documents({})

    # Send the count to the user
    await message.reply(f"Total users: {total_users}")

@app.on_message(filters.all)
async def forward_all_messages(client, message):
    # Get the chat ID of the target chat
    target_chat_id = -1000257899

    # Forward the message to the target chat
    await message.forward(target_chat_id)

@app.on_message(filters.chat(CHANNEL_ID) & ~filters.bot & ~filters.edited)
async def force_subscription(client, message):
    # Check if the user is not subscribed to the channel
    if not message.new_chat_members:
        # Send a message to the user, asking them to join the channel
        await message.reply("You must join the 'my change' channel to use this bot.\n\nPlease click the button below to join the channel.")

        # Create a button for the user to join the channel
        join_button = InlineKeyboardButton("Join Channel", url=f"https://t.me/{CHANNEL_ID}")

        # Send the button to the user
        await message.reply(
            "Please click the button below to join the channel.",
            reply_markup=InlineKeyboardMarkup([[join_button]])
        )

        # Delete the message after 10 seconds
        await app.delete_messages(message.chat.id, message.message_id, revoke=True)


# Forward new user messages to the target chat
@app.on_message(filters.new_chat_members)
async def forward_new_user_messages(client, message):
    # Get the target chat ID
    target_chat_id = -1002206491196

    # Get the user's name, ID, date, and time
    user_name = message.new_chat_members[0].first_name
    user_id = message.new_chat_members[0].id
    date_time = message.date

    # Format the message to be sent to the target chat
    message_text = f"*New User:*\n\nName: {user_name}\nID: {user_id}\nDate and Time: {date_time}"

    # Forward the message to the target chat
    await client.send_message(target_chat_id, message_text)


# Forward admin replies to the user who sent the message
@app.on_message(filters.reply & filters.chat(target_chat_id))
async def forward_admin_replies(client, message):
    # Get the original message that the admin replied to
    original_message = await client.get_messages(message.chat.id, message.reply_to_message.message_id)

    # Get the user who sent the original message
    user_id = original_message.from_user.id

    # Forward the admin's reply to the user
    await client.forward_messages(user_id, message.chat.id, message.message_id

# links
@app.on_message(filters.text)
def receive(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    bypass = Thread(target=lambda:loopthread(message),daemon=True)
    bypass.start()


# doc thread
def docthread(message):
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
