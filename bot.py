import os
import logging
import asyncio
import traceback
import html
import json
import tempfile
import pydub
from pathlib import Path
from datetime import datetime

import telegram
from telegram import (
    Update,
    User,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    BotCommand
)
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackContext,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    AIORateLimiter,
    filters
)
from telegram.constants import ParseMode, ChatAction
from db import *
from theai import *
from models import *

import json
import tempfile
import pydub
from pathlib import Path
import sys
sys.path.append('/path/to/ffmpeg')

logger = logging.getLogger(__name__)


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)





##########################start_handle###################
async def start(update: Update, context: CallbackContext):
    user_name = update.message.from_user.first_name
    if not check_if_user_exists(update.message.from_user):
        create_new_user(update.message.from_user)

        start_msg = f"👋 Hello, {user_name}! I am <b>Anmol Ki AI bot 🤖</b>, your personal assistant. I am here to help you with anything you need.\n\nHere are the <b>commands</b> you can use to interact with me:\n\n🟢 /retry - Regenerate last bot answer\n🟢 /new - Start a new conversation\n🟢 /mode - Select chat mode\n🟢 /help - Show help\n🟢 /subscribe - Subscribe to premium\n🟢 /profile - Check your profile\n\nFeel free to ask me anything!"

        await context.bot.send_message(chat_id=update.effective_chat.id, text=start_msg, parse_mode=ParseMode.HTML)

    else:
        selected_models = fetch_current_model(update.message.from_user.id)

        start_msg = f"👋 Welcome back, {user_name}! I am still <b>Anmol Ki AI bot 🤖</b>, and I'm here to assist you. Currently, You are using the <b>{selected_models}</b> model.\n\nHere are the <b>commands</b> you can use to interact with me:\n\n🟢 /retry - Regenerate last bot answer\n🟢 /new - Start a new conversation\n🟢 /mode - Select chat mode\n🟢 /help - Show help\n🟢 /subscribe - Subscribe to premium\n🟢 /profile - Check your profile\n\nHow may I assist you?"

        await context.bot.send_message(chat_id=update.effective_chat.id, text=start_msg, parse_mode=ParseMode.HTML)


#############################Help_handle########################
async def help(update: Update, context: CallbackContext):
  if not check_if_user_exists(update.message.from_user):
    create_new_user(update.message.from_user)
  help_text = "Here are the <b>commands</b> you can use to interact with me:\n\n🟢 /retry – Regenerate last bot answer\n🟢 /new – Start new dialog\n🟢 /mode – Select chat mode\n🟢 /help – Show help\n🟢 /subscribe - Subscribe to Premium\n🟢 /profile - Check your details\nFeel free to ask me anything!"
  await context.bot.send_message(chat_id=update.effective_chat.id, text=help_text, parse_mode=ParseMode.HTML)


############################promp_handle#########################

async def user_prompt(update: Update, context: CallbackContext,other_func_msg=None):

    times_used = get_times_used(update.message.from_user.id)
    first_time = is_first_time_user(update.message.from_user.id)

    if not check_if_user_exists(update.message.from_user):
        create_new_user(update.message.from_user)
        await update.message.reply_text("<b>We apologize for the inconvenience, could you please repeat your request?</b> 🙇‍♂️")

    if not is_user_subscribed(update.message.from_user):
        await update.message.reply_text("<b>We apologize, but it appears that you are currently not subscribed to our services.</b> 🚫\nTo subscribe, please use the /subscribe command.", parse_mode=ParseMode.HTML)

    elif first_time == True and times_used > 50:
        await update.message.reply_text("<b>We apologize, but it seems that you have exhausted your free trial usage. To continue using our services, please subscribe.</b> 💰🔒\nTo subscribe, please use the /subscribe command.", parse_mode=ParseMode.HTML)

    else:
      
      try:
        # send placeholder message to user
          placeholder_message = await update.message.reply_text("...", parse_mode=ParseMode.HTML)
          # send typing action
          await update.message.chat.send_action(action="typing")
          
          model = fetch_current_model(update.message.from_user.id)
          prev_msgs= fetch_last_three_conversation(update.message.from_user.id)
          the_msg=""
          if update.message.text==None:
             the_msg=other_func_msg
          elif other_func_msg==None:
             the_msg=update.message.text
          entry_of_dialogs(update.message.from_user.id, update.message.id, "user", the_msg)
  ##########################somedata
          reply = chatGpt.ask_shriya(the_msg, update.message.from_user.id, model,prev_msgs)
          prev_answer = ""
          async for gen_item in reply:
            status, answer = gen_item
            answer = answer[:4096]  # telegram message limit
                 # update only when 100 new symbols are ready
            if abs(len(answer) - len(prev_answer)) < 100 and status != "finished":
              continue
            try:
              await context.bot.edit_message_text(answer, chat_id=placeholder_message.chat_id, message_id=placeholder_message.message_id, parse_mode=ParseMode.HTML)
            except telegram.error.BadRequest as e:
              if str(e).startswith("Message is not modified"):
                continue
              else:
                await context.bot.edit_message_text(answer, chat_id=placeholder_message.chat_id, message_id=placeholder_message.message_id)
  
            await asyncio.sleep(0.01)  # wait a bit to avoid flooding
            prev_answer = answer
          entry_of_dialogs(update.message.from_user.id,update.message.id,"assistant",prev_answer)
      except Exception as e:
        error_text = f"Something went wrong during completion. Reason: {e}"
        logger.error(error_text)
        await update.message.reply_text(error_text)
        return
      
        


#####################profile############################
async def profile(update: Update, context: CallbackContext):
    # get user information
    user = update.message.from_user
    username = user.username or "N/A"
    user_id = user.id
    first_name = user.first_name
    days_left = check_days_left(user)

    # create message text with user info
    message_text = f"👤 User Info:\n\n"
    message_text += f"Username: @{username}\n"
    message_text += f"User ID: {user_id}\n"
    message_text += f"First Name: {first_name}\n"
    message_text += f"Days Left: {days_left}"

    # send message
    await update.message.reply_text(message_text)


###########################subscribe######################

async def subscribe(update: Update, context: CallbackContext):
    datas = is_first_time_user(update.message.from_user.id)

    if is_user_subscribed(update.message.from_user) and datas == False:
        dayz_left = check_days_left(update.message.from_user)
        await update.message.reply_text(f"<b>You have already subscribed and have {dayz_left} days left.</b> ✅🗓️", parse_mode=ParseMode.HTML)

    else:
        if check_if_has_phonenemail(update.message.from_user.id):
            data = get_phone_email(update.message.from_user.id)
            phone = data["phone"]
            email = data["email"]

            await update.message.reply_text("<b>To subscribe, please click on the following button:</b> 💳", reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(text='PayU', url=f'http://anmol.serverdock.in/payu/?amnt=10.00&fnm={update.message.from_user.first_name}&em={email}&phn={phone}&id={update.message.from_user.id}&stripe={False}')],
                [InlineKeyboardButton(text='Stripe', url=f'http://anmol.serverdock.in/payu/?amnt=10.00&fnm={update.message.from_user.first_name}&em={email}&phn={phone}&id={update.message.from_user.id}&stripe={True}')],
            ]),parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text("<b>Please register your phone number and email to proceed with subscription.</b> 📝", reply_markup=InlineKeyboardMarkup([    [InlineKeyboardButton(text='Register Details', url=f'https://anmol.serverdock.in/change/?id={update.message.from_user.id}')]]), parse_mode=ParseMode.HTML)



#####################modes#####################
async def show_chat_modes_handle(update: Update, context: CallbackContext):
  await update.message.reply_text("<b>Here are available Chat Modes...</b> 💬", parse_mode=ParseMode.HTML)
  keyboard=[]
  for model in the_models:
    keyboard.append([InlineKeyboardButton(model, callback_data = f"set_chat_mode|{model}")])
  reply_markup = InlineKeyboardMarkup(keyboard)
  await update.message.reply_text("<b>Select Chat Modes:</b> ⚙️", reply_markup=reply_markup, parse_mode=ParseMode.HTML)



#######################CallBack#####################
async def set_chat_mode_handle(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user.id

    query = update.callback_query
    await query.answer()

    chat_mode = query.data.split("|")[1]
    update_current_model(query.from_user.id,chat_mode)
    await query.edit_message_text(f"<b>Hi {query.from_user.username}, I'm {chat_mode}. What can I do for you?</b> 🤖", parse_mode=ParseMode.HTML)




#########################new##################
async def new(update:Update,context:CallbackContext):
  await update.message.reply_text("<b>Starting new dialog ✅</b> 🔄", parse_mode=ParseMode.HTML)
  update_current_model(update.message.from_user.id,"General Assistant")
  await update.message.reply_text("<b>👩🏼‍🎓 Hi, General Assistant. Your AI Assistant. How can I help you?</b> 💡", parse_mode=ParseMode.HTML)


async def retry(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    times_used = get_times_used(user_id)
    first_time = is_first_time_user(user_id)

    if not check_if_user_exists(update.message.from_user):
        create_new_user(update.message.from_user)
        await update.message.reply_text("<b>Sorry, can you ask again?</b> 🤷‍♀️", parse_mode='HTML')

    if not is_user_subscribed(update.message.from_user):
        await update.message.reply_text("<b>Sorry, you are out of subscription 🥹. \nTo subscribe use /subscribe command</b> 💸", parse_mode='HTML')

    elif first_time and times_used > 50:
        await update.message.reply_text("<b>Sorry, you have used your free trial.</b> 🆘 \n<b>Please subscribe to continue. 🥹. To subscribe use /subscribe command</b> 💳", parse_mode='HTML')

    else:
        last_ques = get_last_question(user_id)
        model = fetch_current_model(user_id)
        await user_prompt(update,context,other_func_msg=last_ques)



#############################settings###################################
async def show_settings(update: Update, context: CallbackContext):
    await update.message.reply_text("Chat GPT is a well-known model. It's fast and cheap, ideal for everyday tasks. If there are some tasks it can't handle, try GPT-4.\n\n🟢🟢🟢⚪️⚪️ - Smart\n🟢🟢🟢🟢🟢 - Fast\n🟢🟢🟢🟢🟢 - Cheap\n\nSelect a model:")
    keyboard = [
        [
            InlineKeyboardButton("GPT-3.5", callback_data="set_settings|3.5"),
            InlineKeyboardButton("GPT-4", callback_data="set_settings|4"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Select a model:", reply_markup=reply_markup)


########################voice_message_handle#####################
async def voice_message_handle(update: Update, context: CallbackContext):
    times_used = get_times_used(update.message.from_user.id)
    first_time = is_first_time_user(update.message.from_user.id)

    if not check_if_user_exists(update.message.from_user):
        create_new_user(update.message.from_user)
        await update.message.reply_text("Sorry, something went wrong. Please try again.")

    if not is_user_subscribed(update.message.from_user):
        await update.message.reply_text("Sorry, you are not subscribed 🥺. To subscribe, use the command /subscribe.")

    elif first_time and times_used > 50:
        await update.message.reply_text("Sorry, you have exceeded the free trial limit. 😔 Please subscribe to continue using this service. To subscribe, use the command /subscribe.")

    else:
        user_id = update.message.from_user.id

        voice = update.message.voice
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_dir = Path(tmp_dir)
            voice_ogg_path = tmp_dir / "voice.ogg"

            # download
            voice_file = await context.bot.get_file(voice.file_id)
            await voice_file.download_to_drive(voice_ogg_path)

            # convert to mp3
            voice_mp3_path = tmp_dir / "voice.mp3"
            pydub.AudioSegment.from_file(voice_ogg_path).export(voice_mp3_path, format="mp3")

            # transcribe
            with open(voice_mp3_path, "rb") as f:
                transcribed_text = await transcribe_audio(f)
        text = f"🎤: <i>{transcribed_text}</i>"
        
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
        await user_prompt(update,context,other_func_msg=transcribed_text)
        


if __name__ == '__main__':
    application = ApplicationBuilder().token('').build()
  # add handlers
    user_filter = filters.ALL


    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    new_handler = CommandHandler('new', new)
    application.add_handler(new_handler)
    help_handler = CommandHandler('help', help)
    application.add_handler(help_handler)
    application.add_handler(CommandHandler("mode", show_chat_modes_handle, filters=user_filter))
    application.add_handler(CommandHandler('profile', profile))
    application.add_handler(CommandHandler('subscribe', subscribe))
    application.add_handler(CommandHandler('retry', retry))
#    application.add_handler(CommandHandler('settings', show_settings))
    application.add_handler(MessageHandler(filters.VOICE & user_filter, voice_message_handle))
    application.add_handler(CallbackQueryHandler(set_chat_mode_handle, pattern="^set_chat_mode"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, user_prompt))


    application.run_polling(allowed_updates=Update.ALL_TYPES)

