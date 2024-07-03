import telebot
import time 
import random
from datetime import datetime, timedelta
from time import sleep
import re
import requests
from pymongo import MongoClient
import json

from telebot.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton,InlineKeyboardMarkup,ReplyKeyboardRemove

bot_token = "6818009167:AAF7ilgqpul66bhzyeDZ9yZOkwsDwNVe_Xc" # bot token here from @botfather
Contract = "N/A"
bot = telebot.TeleBot(bot_token)

mongo_cli = MongoClient('mongodb+srv://celo:advbot0n@cluster0.abfjjdi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0') #mongodb uri form mondodb.com


admin_chat_id = 2056940619 # admin id
db = mongo_cli['celoo'] #database name

required_channels = ["@Airdrop_hunters4", "@Airdrop_Looters2", "@Airdrop_Hunters8", "@Airdroplooter8", "@RealAirdrop_payouts"] # check command channel id or username 

def chat_member(user_id):
    for channel in required_channels:
        status = bot.get_chat_member(channel, user_id).status
        # print(status)
        if status not in ['member', 'administrator', 'creator']:
            return False
    return True

buttons = {
    'balance_btn': '🆔 Account',
    'referral_btn': '🙌🏻 Referrals',
    'bonus_btn': '🎁 Bonus',
    'withdraw_btn': '💸 Withdraw',
    'uselful_btn': '🌐 useful information',
    'back_btn': 'BACK'
}

def menu_markup():
    menu_button = ReplyKeyboardMarkup(resize_keyboard=True)
    
    m_button1 = KeyboardButton(buttons['balance_btn'])
    m_button2 = KeyboardButton(buttons['referral_btn'])
    m_button3 = KeyboardButton(buttons['bonus_btn'])
    m_button4 = KeyboardButton(buttons["withdraw_btn"])
    m_button100 = KeyboardButton(buttons["uselful_btn"])

    menu_button.add(m_button1)
    menu_button.add(m_button2, m_button3)
    menu_button.add(m_button4)

    return menu_button


def menu(user_id):
    settings = db.settings.find_one({'user_id':'global'})
    cur = settings.get("currency",None)
    bonus = settings.get("bonus",None) 
    ref_bonus = settings.get("ref_bonus",None)
    bot_username = settings.get("bot_username")
    ref_link = f"https://t.me/{bot_username}?start={user_id}"
    
    start_message = f"<b>🌟 Claim {ref_bonus} {cur} Per Refferal\n{ref_link}</b>"

    bot.send_message(chat_id=user_id, text= start_message,reply_markup=menu_markup(),parse_mode="HTML")
    
################### ADMIN PANEL CODE ###################

def admin_markup():
    admin_panel_markup = InlineKeyboardMarkup()
    
    admin_p_but1 = InlineKeyboardButton(text="Ban", callback_data="ban_user")
    admin_p_but2 = InlineKeyboardButton(text="Unban", callback_data="unban_user")
    admin_p_but3 = InlineKeyboardButton(text="Add Balance", callback_data="add_balance")
    admin_p_but4 = InlineKeyboardButton(text="Cut Balance", callback_data="cut_balance")
    admin_p_but5 = InlineKeyboardButton(text="Get User Data", callback_data="get_data")
    admin_p_but6 = InlineKeyboardButton(text="Bot Settings", callback_data="bot_settings")
    admin_p_but7 = InlineKeyboardButton(text="AutoPay Settings", callback_data="autopay_settings")
    admin_p_but8 = InlineKeyboardButton(text="Withdraw Status", callback_data="withdraw_status")
    
    admin_panel_markup.add(admin_p_but1,admin_p_but2)
    admin_panel_markup.add(admin_p_but3,admin_p_but4,admin_p_but5)
    admin_panel_markup.add(admin_p_but6,admin_p_but7)
    admin_panel_markup.add(admin_p_but8)
    
    return admin_panel_markup

def faucet_setting_markup():
    faucet_markup = InlineKeyboardMarkup()
    f_but1 = InlineKeyboardButton(text="Currency",callback_data="faucet_currency")
    f_but2 = InlineKeyboardButton(text="Api Key",callback_data="faucet_apiKey")
    f_but3 = InlineKeyboardButton(text="Return To Admin Panel", callback_data="return_admin_panel")
    faucet_markup.add(f_but1,f_but2)
    faucet_markup.add(f_but3)
    
    return faucet_markup

@bot.callback_query_handler(func=lambda call: call.data.split()[0] == "autopay_settings")
def handle_autopay_settings(call):
    bot.edit_message_text(chat_id=call.from_user.id, text="Welcome to autopay settings", reply_markup=faucet_setting_markup(), message_id=call.message.message_id)
    
####################
    
def bot_settings_markup():
    bot_setting_markup = InlineKeyboardMarkup()
    
    admin_p_but1 = InlineKeyboardButton(text="Currency", callback_data="setup_currency")
    admin_p_but2 = InlineKeyboardButton(text="Pay Channel", callback_data="setup_pay_channel")
    admin_p_but6 = InlineKeyboardButton(text="Bonus", callback_data="setup_bonus")
    admin_p_but7 = InlineKeyboardButton(text="Referral bonus", callback_data="setup_ref_bonus")
    admin_p_but3 = InlineKeyboardButton(text="Min Withdraw", callback_data="setup_min_withdraw")
    admin_p_but4 = InlineKeyboardButton(text="Max Withdraw", callback_data="setup_max_withdraw")
    admin_p_but8 = InlineKeyboardButton(text="Bot Username", callback_data="setup_bot_username")
    admin_p_but9 = InlineKeyboardButton(text="Return To Admin Panel", callback_data="return_admin_panel")
    bot_setting_markup.add(admin_p_but8)
    bot_setting_markup.add(admin_p_but1,admin_p_but2)
    bot_setting_markup.add(admin_p_but6,admin_p_but7)
    bot_setting_markup.add(admin_p_but3,admin_p_but4)
    bot_setting_markup.add(admin_p_but9)
    
    return bot_setting_markup

# ADMIN PANEL
@bot.message_handler(commands=['admin_panel'])
def admin_panel(message):
    user_id = message.from_user.id
    settings = db.settings.find_one({'user_id':'global'})
    
    if admin_chat_id != user_id:
        return

    admin_panel_msg = f"<b>{message.from_user.first_name}</b>, Welcome to admin panel ->"
    bot.send_message(user_id,admin_panel_msg,parse_mode="html",reply_markup=admin_markup())
####################

# Admin Panel Return 👇
@bot.callback_query_handler(func=lambda call: call.data.split()[0] == "return_admin_panel")
def return_admin_panel(call):
    admin_panel_msg = f"<b>{call.from_user.first_name}</b>, Welcome to admin panel ->"
    bot.edit_message_text(chat_id=call.from_user.id,message_id=call.message.message_id,text=admin_panel_msg,reply_markup=admin_markup(),parse_mode="HTML")
####################'

# WITHDRAW STATUS
@bot.callback_query_handler(func=lambda call: call.data.split()[0] == "withdraw_status")
def handle_withdraw_status(call):
    user_id = call.from_user.id
    settings = db.settings.find_one({'user_id':'global'})
    current_withdraw_status = settings.get("withdraw_status","off")

    btn_text = "Withdraw On" if current_withdraw_status == "off" else "Withdraw Off"
    response_text = f"Withdrawal status is currently {current_withdraw_status.upper()}."

    markup = InlineKeyboardMarkup(row_width=1)
    btn_withdraw = InlineKeyboardButton(btn_text, callback_data="withdraw_toggle")
    btn_return_admin_panel = InlineKeyboardButton("Return to Admin Panel", callback_data="return_admin_panel")
    markup.add(btn_withdraw, btn_return_admin_panel)

    bot.edit_message_text(chat_id=user_id, text=response_text, reply_markup=markup, message_id=call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data == "withdraw_toggle")
def handle_withdraw_toggle(call):
    user_id = call.from_user.id
    settings = db.settings.find_one({'user_id':'global'})
    current_withdraw_status = settings.get("withdraw_status","off")

    new_status = "on" if current_withdraw_status == "off" else "off"
    db.settings.update_one({'user_id':"global"},{'$set':{'withdraw_status':new_status}},upsert=True)
    btn_text = "Withdraw On" if new_status == "off" else "Withdraw Off"
    response_text = f"Withdrawal status set to {new_status.upper()}."

    markup = InlineKeyboardMarkup(row_width=1)
    btn_withdraw = InlineKeyboardButton(btn_text, callback_data="withdraw_toggle")
    btn_return_admin_panel = InlineKeyboardButton("Return to Admin Panel", callback_data="return_admin_panel")
    markup.add(btn_withdraw, btn_return_admin_panel)

    bot.edit_message_text(chat_id=user_id, text=response_text, reply_markup=markup, message_id=call.message.message_id)
####################


# setup fiat currency 👇
@bot.callback_query_handler(func=lambda call: call.data.split()[0] == "faucet_currency")
def handle_pay_currency(call):
    user_id = call.from_user.id
    bot.edit_message_text(chat_id = user_id,message_id=call.message.message_id,text="*Enter the currency code from faucet pay ->*\n\n/cancel -> for back",parse_mode="markdown")
    bot.register_next_step_handler(call.message,setup_faucet_currency)
    
def setup_faucet_currency(message):
    if message.text == "/cancel":
        bot.send_message(message.from_user.id,f"<b>{message.from_user.first_name}</b>, Welcome to admin panel ->",reply_markup=admin_markup(),parse_mode="HTML")
        return
    
    faucet_currency = message.text
    db.settings.update_one({'user_id':"global"},{'$set':{'faucet_currency':faucet_currency}},upsert=True)
    bot.send_message(message.from_user.id,f"Done!! Auto Pay Currency set to -> *{faucet_currency}*",reply_markup= faucet_setting_markup(),parse_mode="markdown")
####################

# setup facuet pay api key 👇
@bot.callback_query_handler(func=lambda call: call.data.split()[0] == "faucet_apiKey")
def handle_pay_api(call):
    user_id = call.from_user.id
    bot.edit_message_text(chat_id = user_id,message_id=call.message.message_id,text="*Enter the api key from faucet pay ->*\n\n/cancel -> for back",parse_mode="markdown")
    bot.register_next_step_handler(call.message,setup_faucet_api)
    
def setup_faucet_api(message):
    if message.text == "/cancel":
        bot.send_message(message.from_user.id,f"<b>{message.from_user.first_name}</b>, Welcome to admin panel ->",reply_markup=admin_markup(),parse_mode="HTML")
        return
    
    faucet_apiKey = message.text
    db.settings.update_one({'user_id':"global"},{'$set':{'faucet_apiKey':faucet_apiKey}},upsert=True)
    bot.send_message(message.from_user.id,f"Done!! faucetpay api key set to -> *{faucet_apiKey}*",reply_markup= faucet_setting_markup(),parse_mode="markdown")
####################

# add balance 👇
@bot.callback_query_handler(func=lambda call: call.data.split()[0] == "add_balance")
def handle_add_balance(call):
    user_id = call.from_user.id
    bot.edit_message_text(chat_id = user_id,message_id=call.message.message_id,text="*Enter the UserId and Balance in this format for add balance in user balance ->*\n\n`userid:amount` *||* `5337150824:10`\n\n/cancel -> for back",parse_mode="markdown")
    bot.register_next_step_handler(call.message,add_user_balance)
    
def add_user_balance(message):
    if message.text == "/cancel":
        bot.send_message(message.from_user.id,f"<b>{message.from_user.first_name}</b>, Welcome to admin panel ->",reply_markup=admin_markup(),parse_mode="HTML")
        return
    
    user_id,amount = message.text.split(":")
    db.users.update_one({'user_id':int(user_id)},{'$inc':{'balance':float(amount)}},upsert=True)
    bot.send_message(message.from_user.id,f"Done:- {amount} added to {user_id}",reply_markup= admin_markup())
####################
    
# cut balance 👇
@bot.callback_query_handler(func=lambda call: call.data.split()[0] == "cut_balance")
def handle_cut_balance(call):
    user_id = call.from_user.id
    bot.edit_message_text(chat_id = user_id,message_id=call.message.message_id,text="*Enter the UserId and Balance in this format for cut user balance ->*\n\n`userid:amount` *||* `5337150824:10`\n\n/cancel -> for back",parse_mode="markdown")
    bot.register_next_step_handler(call.message,cut_user_balance)
    
def cut_user_balance(message):
    if message.text == "/cancel":
        bot.send_message(message.from_user.id,f"<b>{message.from_user.first_name}</b>, Welcome to admin panel ->",reply_markup=admin_markup(),parse_mode="HTML")
        return
    
    user_id,amount = message.text.split(":")
    amo = float(amount)
    db.users.update_one({'user_id':int(user_id)},{'$inc':{'balance':amo}},upsert=True)
    bot.send_message(message.from_user.id,f"Done:- {amount} cuted from {user_id}",reply_markup= admin_markup())
####################

# banuser 👇
@bot.callback_query_handler(func=lambda call: call.data.split()[0] == "ban_user")
def handle_ban_user(call):
    user_id = call.from_user.id
    bot.edit_message_text(chat_id = user_id,message_id=call.message.message_id,text="*Enter the userid whom you want to ban ->*\n\n/cancel -> for back",parse_mode="markdown")
    bot.register_next_step_handler(call.message,ban_user)
    
def ban_user(message):
    if message.text == "/cancel":
        bot.send_message(message.from_user.id,f"<b>{message.from_user.first_name}</b>, Welcome to admin panel ->",reply_markup=admin_markup(),parse_mode="HTML")
        return
    user_id = message.text
    db.users.update_one({'user_id':int(user_id)},{'$set':{'status':1}},upsert=True)
    bot.send_message(message.from_user.id,f"Done!! user banned -> *{user_id}*",reply_markup= admin_markup(),parse_mode="markdown")
####################

# unbanuser 👇
@bot.callback_query_handler(func=lambda call: call.data.split()[0] == "unban_user")
def handle_unban_user(call):
    user_id = call.from_user.id
    bot.edit_message_text(chat_id = user_id,message_id=call.message.message_id,text="*Enter the userid whom you want to unban ->*\n\n/cancel -> for back",parse_mode="markdown")
    bot.register_next_step_handler(call.message,unban_user)
    
def unban_user(message):
    if message.text == "/cancel":
        bot.send_message(message.from_user.id,f"<b>{message.from_user.first_name}</b>, Welcome to admin panel ->",reply_markup=admin_markup(),parse_mode="HTML")
        return
    user_id = message.text
    db.users.update_one({'user_id':int(user_id)},{'$set':{'status':0}},upsert=True)
    bot.send_message(message.from_user.id,f"Done!! user unbanned -> *{user_id}*",reply_markup= admin_markup(),parse_mode="markdown")
####################
   
def format_setting(name, value):
    check_mark = "✅" if value is not None else "❌"
    return f"{check_mark} <b>{name}</b> -> <code>{value}</code>"

def handle_setting(call, setting_name, setting_key):
    user_id = call.from_user.id
    bot.edit_message_text(chat_id=user_id, message_id=call.message.message_id,
                          text=f"*Enter the {setting_name} ->*\n\n/cancel -> for back", parse_mode="markdown")
    bot.register_next_step_handler(call.message, lambda message: set_setting(message, setting_key,setting_name))

def set_setting(message, setting_key,setting_name):
    if message.text == "/cancel":
        bot.send_message(message.from_user.id, f"<b>{message.from_user.first_name}</b>, Welcome to admin panel ->",reply_markup=admin_markup(), parse_mode="HTML")
        return

    value = message.text
    
    db.settings.update_one({'user_id':'global'},{'$set':{setting_key:value}},upsert=True)
    bot.send_message(message.from_user.id, f"Done!! {setting_name} set to -> <b>{value}</b>",
                     reply_markup=admin_markup(), parse_mode="html")

# Callback data to setting mappings
setting_callbacks = {
    "setup_currency": ("Currency", "currency"),
    "setup_pay_channel": ("Payment Channel", "pay_channel"),
    "setup_bonus": ("Bonus", "bonus"),
    "setup_ref_bonus": ("Referral Bonus", "ref_bonus"),
    "setup_min_withdraw": ("Minimum Withdraw", "min_with"),
    "setup_max_withdraw": ("Maximum Withdraw", "max_with"),
    "setup_bot_username": ("Bot Username", "bot_username"),
}

# Settings Panel
@bot.callback_query_handler(func=lambda call: call.data.split()[0] == "bot_settings")
def settings_panel(call):
    user_id = call.from_user.id
    settings_doc = db.settings.find_one({'user_id': 'global'})
    
    if settings_doc:
        admin_panel_msg = (
            f"<b>{call.from_user.first_name}</b>, Welcome to Bot Settings panel ->\n\n"
            f"{format_setting('Currency', settings_doc.get('currency', ''))}"
            f"\n{format_setting('Payment Channel', settings_doc.get('pay_channel', ''))}"
            f"\n{format_setting('Bonus', settings_doc.get('bonus', ''))}"
            f"\n{format_setting('Referral Bonus', settings_doc.get('ref_bonus', ''))}"
            f"\n{format_setting('Minimum Withdraw', settings_doc.get('min_with', ''))}"
            f"\n{format_setting('Maximum Withdraw', settings_doc.get('max_with', ''))}"
            f"\n{format_setting('Bot UserName', settings_doc.get('bot_username', ''))}"
        )
        bot.edit_message_text(chat_id=user_id, text=admin_panel_msg, message_id=call.message.message_id, parse_mode="html", reply_markup=bot_settings_markup())
    else:
        bot.send_message(user_id, "Settings not found.", parse_mode="html", reply_markup=bot_settings_markup())

def format_setting(setting_name, setting_value):
    return f"<b>{setting_name}:</b> {setting_value or 'Not set'}"

# Handle each setting callback
@bot.callback_query_handler(func=lambda call: call.data.split()[0] in setting_callbacks)
def handle_setting_callback(call):
    setting_name, setting_key = setting_callbacks[call.data.split()[0]]
    handle_setting(call, setting_name, setting_key)


############################## END ADMIN PANEL CODE ##############################

@bot.message_handler(commands=['broadcast'])
def send_broadcast(message):
    if message.chat.id == admin_chat_id:
        bot.send_message(message.chat.id, "Send Your Broadcast Message With HTMl")
        bot.register_next_step_handler(message, send_broadcast2)
    else:
        return

def send_broadcast2(message):
    user_ids = [user["user_id"] for user in db.users.find({}, {"user_id": 1})]
    for user_id in user_ids:
        try:
            message_id = bot.send_message(user_id, message.text,parse_mode="HTML")
            bot.pin_chat_message(chat_id=user_id, message_id=message_id.message_id)
            time.sleep(1)
        except Exception as e:
            return
            # print(f"Hata: {e}")

@bot.message_handler(commands=['broadcastwithbtn'])
def send_broadcast_with_btn(message):
    if message.chat.id == admin_chat_id:
        bot.send_message(message.chat.id, "Send Your Broadcast Message With HTML")
        bot.register_next_step_handler(message, send_broadcast_with_btn2)
    else:
        return

def send_broadcast_with_btn2(message):
    try:
        broadcast_info = {
            "msg": message.text,
            "btn_txt": "",
            "btn_url":"",
            "pic_url": ""
        }
        with open("broadcast_info.json", "w") as json_file:
            json.dump(broadcast_info, json_file)

        bot.send_message(message.chat.id, "Send Your Broadcast Button Text")
        bot.register_next_step_handler(message, send_broadcast_with_btn3)

    except Exception as e:
        print(f"Hata: {e}")

def send_broadcast_with_btn3(message):
    try:
        with open("broadcast_info.json", "r") as json_file:
            broadcast_info = json.load(json_file)
            broadcast_info["btn_txt"] = message.text

        with open("broadcast_info.json", "w") as json_file:
            json.dump(broadcast_info, json_file)

        bot.send_message(message.chat.id, "Send Your Broadcast Button URL")
        bot.register_next_step_handler(message, send_broadcast_with_btn4)

    except Exception as e:
        print(f"Hata: {e}")

def send_broadcast_with_btn4(message):
    try:
        with open("broadcast_info.json", "r") as json_file:
            broadcast_info = json.load(json_file)
            broadcast_info["btn_url"] = message.text

        with open("broadcast_info.json", "w") as json_file:
            json.dump(broadcast_info, json_file)

        bot.send_message(message.chat.id, "Send Your Broadcast Photo URL")
        bot.register_next_step_handler(message, send_broadcast_with_btn5)

    except Exception as e:
        print(f"Hata: {e}")

def send_broadcast_with_btn5(message):
    try:
        with open("broadcast_info.json", "r") as json_file:
            broadcast_info = json.load(json_file)
            broadcast_info["pic_url"] = message.text

        with open("broadcast_info.json", "w") as json_file:
            json.dump(broadcast_info, json_file)

        user_ids = [user["user_id"] for user in db.users.find({}, {"user_id": 1})]
        for user_id in user_ids:
            try:
                inline_keyboard = InlineKeyboardMarkup(row_width=2)
                button = [
                    InlineKeyboardButton(broadcast_info["btn_txt"], url=broadcast_info['btn_url'])
                ]
                inline_keyboard.add(*button)

                broadcast_message = broadcast_info["msg"]

                if broadcast_info["pic_url"]:
                    message_id = bot.send_photo(user_id, broadcast_info["pic_url"], broadcast_message, parse_mode="HTML", reply_markup=inline_keyboard)
                    bot.pin_chat_message(chat_id=user_id, message_id=message_id.message_id)
                    time.sleep(1)
                else:
                    message_id = bot.send_message(user_id, broadcast_message, parse_mode="HTML", reply_markup=inline_keyboard)
                    bot.pin_chat_message(chat_id=user_id, message_id=message_id.message_id)
                    time.sleep(1)

            except Exception as e:
                # print(f"Hata: {e}")
                return

    except Exception as e:
        return
        # print(f"Hata: {e}")


@bot.message_handler(commands=['status'])
def status_command(message):
    if message.from_user.id == admin_chat_id:
        user_count = db.users.count_documents({})
        bot.send_message(message.chat.id, f"Total users: {user_count}")

def send_join_message(message):
    user_id = message.from_user.id

    if not chat_member(user_id):
        join_channels_message = ("💡 You Must Join Our All Channels To Get Payment\n\n"
        "[@Airdrop_Hunters4](https://t.me/Airdrop_Hunters4)\n"
        "[@AirdropLooter8](https://t.me/AirdropLooter8)\n"
        "[@Airdrop_Looters2](https://t.me/Airdrop_Looters2)\n"
        "[@Airdrop_Hunters8](https://t.me/Airdrop_Hunters8)\n" 
        "[@Airdrop_Hunterrs1](https://t.me/Airdrop_Hunterrs1)\n"                         
        "[@promoter](https://t.me/AirdropNeptune)\n"
        "[@promoter](https://t.me/VerifiedXAirdrop)\n"                    
        "[@payouts](https://t.me/RealAirdrop_payouts)\n\n▫️ Before starting using the Bot"
                                )

        join_but = ReplyKeyboardMarkup(resize_keyboard=True)
        join_but.add(KeyboardButton(text="✅ Joined"))
        bot.send_message(user_id,join_channels_message,parse_mode='Markdown',reply_markup=join_but,disable_web_page_preview=True)
        return
    
    user_data = db.users.find_one({'user_id':user_id})
    email = user_data.get('email',None)

    if not email:
        msg = "<b>Please enter your CELO Address:</b>"
        bot.send_message(user_id, msg, parse_mode="HTML")
        bot.register_next_step_handler(message, set_email_address)
        return
    
    menu(user_id)
    

def set_email_address(message):
    get_settings = db.settings.find_one({'user_id':"global"})

    currency = get_settings.get('currency', None)
    ref_bonus = get_settings.get('ref_bonus', None)

    
    user_id = message.from_user.id
    email = message.text


    # Check if the email is in a valid format
    if not is_valid_email(email):
        bot.send_message(user_id, "*⛔️ Invalid email address!* Please send a valid Gmail address.",parse_mode="markdown")
        bot.register_next_step_handler(message, set_email_address)
        return

    # Check if the email already exists in the users collection
    if db.users.find_one({"email": email}):
        bot.send_message(user_id, f"*⚠️ This wallet address ({email}) is already in use.*", parse_mode="markdown")
        bot.register_next_step_handler(message, set_email_address)
        return

    # Validate the email via FaucetPay
    #if not is_valid_faucetpay_email(email):
        #bot.send_message(user_id, "<b>⛔️ Invalid FaucetPay email address!</b> Please provide a valid <a href='https://faucetpay.io/?r=5085039'>FaucetPay</a> email.",parse_mode="HTML")
        #bot.register_next_step_handler(message, set_email_address)
       # return

    #### Referral Bonus ####
    userData = db.users.find_one({'user_id':user_id})
    
    referred_by =  userData.get("ref_by", None) 
    referred = userData.get("referred",None) 
    
    if referred_by != "none" and referred == None:
        db.users.update_one({'user_id':int(referred_by)},{'$inc':{'balance':float(ref_bonus)}},upsert=True)
        bot.send_message(referred_by, f"*➕ {ref_bonus} {currency} For New Referral*",parse_mode="markdown")
        db.users.update_one({'user_id':user_id},{'$set':{'referred':1}},upsert=True)
    #### end ####
    
    db.users.update_one({'user_id':user_id},{'$set':{'email':email}},upsert=True)
    bot.send_message(user_id, f"*✅ Your CELO Address  Set To:* {email}", parse_mode="markdown")

    menu(user_id)

def is_valid_email(email):
    if len(email) == 42 and email.startswith("0x"):
        return email is not None

#def is_valid_faucetpay_email(email):
    #settings = db.settings.find_one({'user_id':'global'})
    #api_key = settings.get("faucet_apiKey",None)
    # Make a request to FaucetPay API to validate the email
    #api_url = "https://faucetpay.io/api/v1/checkaddress"
    #params = {
        #"api_key": api_key,
       # "address": email
   # }

   # response = requests.post(api_url, data=params)
   # data = response.json()

    # Check if the response status is OK (200) and the email is valid
   # return response.status_code == 200 and data.get("status") == 200
    

    

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = int(message.from_user.id)
    first_name = message.from_user.first_name

    # Track referral
    ref_by = message.text.split()[1] if len(message.text.split()) > 1 and message.text.split()[1].isdigit() else None

    if not db.users.find_one({'user_id': user_id}):
        if ref_by and int(ref_by) != user_id and db.users.find_one({'user_id': int(ref_by)}):
            db.users.update_one({'user_id': user_id}, {'$set': {'user_id': user_id, 'ref_by': int(ref_by)}},upsert=True)
            db.users.update_one({'user_id': int(ref_by)}, {'$inc': {'total_ref': 1}},upsert=True)
        else:
            db.users.update_one({'user_id': user_id}, {'$set': {'user_id': user_id, 'ref_by': "none"}},upsert=True)

    # Check user membership
    send_join_message(message)

    

    
@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_all_commands(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    
    get_settings = db.settings.find_one({'user_id':"global"})
    currency = get_settings.get('currency', None)
    dice_bonus = get_settings.get('dice_bonus', None)
    bonus = get_settings.get('bonus', None)
    ref_bonus = get_settings.get('ref_bonus', None)
    min_with = get_settings.get('min_with', None)
    max_with = get_settings.get('max_with', None)
    bot_username = get_settings.get('bot_username', None)

    userData = db.users.find_one({'user_id':user_id})
    balance = userData.get('balance', 0)
    total_referral = userData.get('total_ref', 0)
    ref_link = f"https://t.me/{bot_username}?start={user_id}"
    email = userData.get('email', None)
    status = userData.get('status',None)
    total_withdraw = userData.get('total_with',0)
    
    if status == 1:
        return
    
    share_button_markup = InlineKeyboardMarkup()
    share_button = share_button_markup.add(InlineKeyboardButton( text= f"🎁 Share and Earn ||  {ref_bonus} {currency}", url= f"https://t.me/share/url?url={ref_link}"))
    
    cancel_back_markup = ReplyKeyboardMarkup(resize_keyboard=True)
    cancel_back_markup.add(KeyboardButton(buttons['back_btn']))
    
#################### Advertise ####################
    if  random.random() < 0.2: # 0.1 show probablity mean 0.1 mean 10% if you add there 0.5 than every 2 or 3 message after come advertise or yu can add any amount there as 
        advertise(message)
    #################### Advertise ####################

    ###############
    if message.text == "✅ Joined":
        send_join_message(message)
         
    ###############

    
    
    ###############
    if message.text == buttons['balance_btn']:
        markup = InlineKeyboardMarkup()
        button = InlineKeyboardButton("🎁🎉 CLAIM Preton 🎉🎁", url="https://t.me/PeaAIBot/Fission?startapp=sid-6684b1c4ff89920011a54029")
        markup.add(button)
        text = (f"<b>✳️ Account Balance</b>\n\n"
        f"<b>🚥 User Name:</b> <code>{message.from_user.first_name}</code>\n\n"
        f"<b>🚥 Total Balance:</b> <b>{balance:.6f} {currency}</b>\n"
        f"<b>🚥 Total Referrals:</b> <code>{total_referral} Users</code>\n\n"
        f"<b>🔥 Claim Free {ref_bonus} {currency} Per Referral</b>")
        bot.send_message(user_id,text,parse_mode="HTML",reply_markup=markup)
        return
    if message.text == buttons['uselful_btn']:
        text = """
🔷 Token Contract: `0xc77d2d650676a920732568f00610777dc945574a`

✅ Name: `Teddy Doge`

💠 Symbol: `TDOGE`

🌐 Network: `VICTON`

🔸Decimal: `18`"""
        bot.send_message(
            message.chat.id, text, parse_mode="markdown")
        return
        
    #############
    
    if message.text == buttons['bonus_btn']:
        user_id = int(message.from_user.id)
    
        advertise(message)

        last_claimed_at = userData.get('bonus_claimed_at',None)
        if last_claimed_at:
            last_claimed_at = datetime.strptime(last_claimed_at, "%Y-%m-%d %H:%M:%S")
            time_since_last_claim = datetime.now() - last_claimed_at
        else:
            time_since_last_claim = timedelta(hours=24)
    
        if time_since_last_claim >= timedelta(hours=24):
            # Update the bonus_claimed_at property with the current time
            db.users.update_one({'user_id':user_id},{'$set':{"bonus_claimed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}},upsert=True)
            bot.send_dice(user_id,'🎳')
            sleep(2)
            db.users.update_one({'user_id':user_id},{'$inc':{'balance':float(bonus)}},upsert=True)
            bot.send_message(user_id, f"*🥁 TON Bonus Success*\n\n🔋 You Earned Free *{bonus} {currency}* Success To Your Account.",  parse_mode="markdown")
        else:
            # Calculate the time until the next claim
            time_until_next_claim = timedelta(hours=24) - time_since_last_claim
            hours, remainder = divmod(time_until_next_claim.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
    
            # Send a message indicating the time until the next claim
            bot.send_message(user_id, f"🕐 You can claim your bonus again in {hours} hours, {minutes} minutes, and  {seconds} seconds.")   
        #######################
  
    #######################
    if message.text == buttons['referral_btn']:

        msg = (f"<b>🚨 Invite Refferals</b>\n\n"
               f"<u>🚀 Invite Real Refferals</u>, Earn Unlimited USDT, The More You Invite The More You Withdraw.\n\n"
               f"<b>🌼 Claim Free <u>{ref_bonus} {currency}</u> Per Refferal</b>\n\n"
               f"<b>Total Refferals: {total_referral} Users</b>\n\n"
               f"<b>Your Refferal Link:</b>\n"
               f"{ref_link}")
       
        bot.send_message(user_id,msg,parse_mode="html",reply_markup=share_button)
    ####################

    
    #######################
    if message.text == buttons['withdraw_btn']:
        if not email:
            bot.send_message(user_id,"*Please update your email address*",parse_mode="markdown")
            return
        
        
        withdraw_staus = get_settings.get('withdraw_status',"off")
        if withdraw_staus == "off":
            bot.send_message(user_id,"Withdraw currently off. Please try again later.")
            return
        
        # if float(balance)<float(min_with):
        #     bot.send_message(user_id,f"*✅ You need at least* \n\n`{min_with} {currency}`\n\n*👋 Share your referral link to increase your balance*",parse_mode="markdown")
        #     return

        withdraw_markup = InlineKeyboardMarkup()
        withdraw_markup.add(InlineKeyboardButton(text="Receive Payouts",callback_data="/withdraw"))
        msg = (f"<b>⛴ Get Instant Payouts</b>\n\n"
        f"<b>🔻 Total Balance:</b> <code>{balance:.6f} {currency}</code>\n"
        f"<b>🔻 {currency} Address:</b> {email}\n\n"
        "<i>💸 Confirm Transactions Instant</i>")
        bot.send_message(user_id,msg,parse_mode="HTML",reply_markup=withdraw_markup)
        #######################

@bot.callback_query_handler(func=lambda call: call.data.split()[0] == "/withdraw")
def withdraw_handler(call):
    user_id = call.from_user.id

    bot.delete_message(user_id,call.message.id)

    bot.send_message(user_id,"📝 Enter Your Amount For Withdraw:")
    bot.register_next_step_handler(call.message,process_withdraw)


def process_withdraw(message):
    user_id = message.from_user.id
    
    get_settings = db.settings.find_one({'user_id':"global"})
    userData = db.users.find_one({'user_id':user_id})

    currency = get_settings.get('currency', None)
    pay_channel = get_settings.get('pay_channel', None)
    min_with = get_settings.get('min_with', None)
    max_with = get_settings.get('max_with', None)
    bot_username = get_settings.get('bot_username', None)
    api_key = get_settings.get('faucet_apiKey', None)
    cur = get_settings.get('faucet_currency', None)
    total_with = userData.get("total_with", 0)
    total_refs = userData.get("total_ref", 0)
    balance = userData.get("balance", 0)
    email  = userData.get("email",None)

    amount = message.text
    
    if message.text == buttons['back_btn']:
        bot.send_message(user_id,"❌ withdraw cancelled",reply_markup=menu_markup())
        return
    
    if not re.match(r'^\d+(\.\d{1,8})?$', amount):
            bot.send_message(user_id, "Invalid withdrawal amount. Please enter a valid number.",reply_markup=menu_markup())
            return
    
    if float(max_with) < float(amount):
        bot.send_message(user_id,f"*❌ Maximum Withdraw:*` {max_with}` *{currency}*",reply_markup=menu_markup(),parse_mode="markdown")
        return
    
    if float(min_with) > float(amount):
        bot.send_message(user_id,f"*❌ Minimum Withdraw:*` {min_with}` *{currency}*",reply_markup=menu_markup(),parse_mode="markdown")
        return
    
    if float(balance) < float(amount):
        bot.send_message(user_id,f"*❌ You Have Only Withdrawal Amount Is:*` {balance:.7f}` *{currency}*",reply_markup=menu_markup(),parse_mode="markdown")
        return
       
    bot.send_message(user_id,f"✅ *Withdrawal Requested*\nYou will receive your payment within 1 - 10 Minutes. \n\n💳 Transaction Details:\n {amount} {currency} to the wallet In 1 / 24 Hours\n*{email}*",parse_mode="markdown",reply_markup=menu_markup())
    
    db.users.update_one({'user_id':user_id},{'$inc':{'total_with':float(amount)}},upsert=True)

    amo = float(amount)
    db.users.update_one({'user_id':user_id},{'$inc':{'balance':-amo}},upsert=True)
    amoooo = str(message.text)
    db.users.update_one({'user_id':user_id},{'$set':{'last_withdraw_at':datetime.now().strftime("%Y-%m-%d %H:%M:%S")}},upsert=True)
    url = f"http://cryptopay-up-apis.me/sendcelopvtltdkp/{amoooo}/{api_key}/{email}"
    dataresp = requests.get(url)
    response = dataresp.json() 
    tx_hash = response['txHash']
    msg = (
    "*✅ Withdrawn Paid Successful*\n\n"
    f"*🤑 Amount:* {float(amount)} {currency}\n"
    f"*🏷️ Address:* {email}\n"
    f"*🔗 TransactionID:* {tx_hash}\n\n"
    f"_Now check your {currency} Wallet to see the transaction._"
    )
    bot.send_message(user_id,msg,parse_mode="markdown")
    markup = InlineKeyboardMarkup()
    button = InlineKeyboardButton("❤️ Claim Extra USDT ", url="https://t.me/PeaAIBot/Fission?startapp=sid-6684b1c4ff89920011a54029")
    markup.add(button)
    text = ("<b>🚀 New Withdrawal Paid!</b>\n\n"
        f"<b>🔰 User :</b> <i>{message.from_user.first_name}</i>\n"
        f"<b>🌐 User Id :</b> <code>{user_id}</code>\n"
        f"<b>♨ User Referrals ::</b> <i>{total_refs}</i>\n"
        f"<b>💲 Amount :</b> <i>{amo} {currency}</i>\n"
        f"<b>🔎 Address  :</b> <code>{email}</code>\n"
        f"<b>🪙 Hash :</b> <a href='https://explorer.celo.org/mainnet/tx/{tx_hash}'>{tx_hash}</a>\n\n"
        f"<b>🔃 Bot Link : @{bot_username}</b>")
    bot.send_message(pay_channel, text, parse_mode="HTML", reply_markup=markup)
    settings = db.settings.find_one({'user_id':'global'})
    bot.send_message(settings.get("admin_id",None),f"Withdrawal failed.\n\nResponse: {response}")
    bot.send_message(user_id,f"Withdraw failed!! Please Try Again Later.")
    
    
    

    
def advertise(message):
    user_id = message.from_user.id
    markup = InlineKeyboardMarkup()
    button = InlineKeyboardButton("🔥 Start Mining TON ", url="https://t.me/preton_drop_bot?start=70172ca6-1e7c-47d3-b8fe-513eb8300a2c")
    markup.add(button)
    pin = bot.send_photo(chat_id = message.chat.id, photo = "https://t.me/DGBBOTSPAYOUT/3" , caption = "<b>✅ You have just won 50000$🤑🤑 </b>\n\n<b>🤑Start the bot below to start earning it.🤑</b>\n\n<b><a href='https://t.me/preton_drop_bot?start=70172ca6-1e7c-47d3-b8fe-513eb8300a2c'>🎁 Start Free TON Mining Now.  </a></b>", reply_markup = markup, parse_mode = "HTML")
    data = db.users.find_one({'user_id':user_id})
    s_p = data.get("s_p")
    
    if s_p == None:
        bot.pin_chat_message(user_id,pin.message_id)
        db.users.update_one({'user_id':user_id},{'$set':{'s_p':1}})    
    
if __name__ == '__main__':
    while True:
        try:
            print("bot is running")
            bot.polling(non_stop=True)
        except Exception as e:
            settings = db.settings.find_one({'user_id':'global'})

            print(f"Error:{e}")
            bot.send_message(admin_chat_id, f"*Error*:\n\n`{e}`",parse_mode="markdown")
            time.sleep(10)
