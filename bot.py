import logging
from telegram import (
    Update,
    User,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    BotCommand
)
from telegram.constants import ParseMode, ChatAction
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
from db import *
from theai import *

import json
import tempfile
import pydub
from pathlib import Path
import sys
sys.path.append('/path/to/ffmpeg')


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


models={"Shriya (AI Assistant)":"An Ai Assistant Named Shriya",
       "Code Assitant":"A code Assitant",
       "Startup Idea Generator":"Startup Idea Generator",
       "Relationship coach":"Relationship Coach",
       "CV Builder":"CV Builder Robot",
       "Teacher":"a Teacer",
       "A.P.J Abdul Kalam":"Dr. A.P.J Abdul Kalam",
       "Albert Einstien":"Albert Einstien",
       "Sandeep Maheshwari":"Sandeep Maheshwari",
       "Narendra Modi":"Narendra Modi"}
the_models = ["Shriya (AI Assistant)","Code Assitant","Startup Idea Generator","Relationship coach","CV Builder","Teacher","A.P.J Abdul Kalam","Albert Einstien","Sandeep Maheshwari","Narendra Modi"]
  


##########################start_handle###################  
async def start(update: Update, context: CallbackContext):
  user_name= update.message.from_user.first_name
  if not check_if_user_exists(update.message.from_user):
    create_new_user(update.message.from_user)
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Hi {user_name} 👋, I am Anmol Ki bot..... Your New Intelligent Assistant And I am here to help you with your regular stuff...\nCommands:\n⚪️ /retry – Regenerate last bot answer\n⚪️ /new – Start new dialog\n⚪️ /modes – Select chat mode\n⚪️ /subscribe – pay subscription fee\n⚪️ /balance – Show balance\n⚪️ /help – Show help\nAnd now... ask me anything!')
  else:
    selected_models=fetch_current_model(update.message.from_user.id)
    
    text=f'Hey {user_name}, Welcome back.\nI am {selected_models} \n What can i do for You?\nCommands:\n⚪️ /retry – Regenerate last bot answer\n⚪️ /new – Start new dialog\n⚪️ /modes – Select chat mode\n⚪️ /profile – Show profile\n⚪️ /subscribe – pay subscription fee\n⚪️ /help – Show help\nAnd now... ask me anything!'
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

#############################Help_handle########################
async def help(update: Update, context: CallbackContext):
  if not check_if_user_exists(update.message.from_user):
    create_new_user(update.message.from_user)
  help_text = "Here are the list of commands which you can use.\n/help : used to get help.\n/subscribe : used to get subscription after subscription ends.\n/profile : used to get Profile Details.\n/profile : used to get profile data\n/new : start new dialog.\n/modes : select modes."
  await context.bot.send_message(chat_id=update.effective_chat.id, text= help_text)

############################promp_handle#########################

async def user_prompt(update: Update,context:CallbackContext):
  times_used=get_times_used(update.message.from_user.id)
  first_time =is_first_time_user(update.message.from_user.id)
  if not check_if_user_exists(update.message.from_user):
    create_new_user(update.message.from_user)
    await update.message.reply_text("Sorry can you ask again?")
  if not is_user_subscribed(update.message.from_user):
    await update.message.reply_text("Sorry, You are out of Subscription 🥹. \nto Subscribe use /subscribe command")
  elif first_time==True and times_used>50:
    await update.message.reply_text("Sorry, You have used your free trail./n Please Subscribe to continue. 🥹. \nTo Subscribe use /subscribe command")
    
  else:
    # send placeholder message to user
    placeholder_message = await update.message.reply_text("...")

    # send typing action
    await update.message.chat.send_action(action="typing")
    update_message_text= update.message.text
    entry_of_dialogs(update.message.from_user.id,update.message.id,"user",update_message_text)
    async def get_reply():
      model = fetch_current_model(update.message.from_user.id)
      reply = ask_shriya(update.message.text,update.message.from_user.id,model)
      return reply
    reply= await get_reply()
    reply=reply.choices[0].message.content
    entry_of_dialogs(update.message.from_user.id,update.message.id,"bot",reply)
    await context.bot.edit_message_text(reply, chat_id=placeholder_message.chat_id, message_id=placeholder_message.message_id)
    
    # entry_of_dialogs(update.message.id,"bot",)
#####################profile############################
async def profile(update:Update,context:CallbackContext):
  left_day=str(check_days_left(update.message.from_user))
  upd = update.message.from_user
  msgdt=f'User Name : {upd.username} Id : {upd.id} Name : {upd.first_name} Days Left :  {left_day}'
  await update.message.reply_text(msgdt)
  
###########################subscribe######################

async def subscribe(update:Update,context:CallbackContext):
  datas=is_first_time_user(update.message.from_user.id)
  if is_user_subscribed(update.message.from_user) and datas==False:
    dayz_left = check_days_left(update.message.from_user)
    await update.message.reply_text(f"You have already Subscribed and you have {dayz_left} days left")
  else:
    
    if check_if_has_phonenemail(update.message.from_user.id):
      data = get_phone_email(update.message.from_user.id)
      phone=data["phone"]
      email=data["email"]
      await update.message.reply_text(f"To Subscribe Go to the Following Button:",reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton(text='PayU', url=f'http://yaallo.zapto.org/payu/?amnt=10.00&fnm={update.message.from_user.first_name}&em={email}&phn={phone}&id={update.message.from_user.id}')],
        [InlineKeyboardButton(text='Stripe', url=f'http://yaallo.zapto.org/payu/?amnt=10.00&fnm={update.message.from_user.first_name}&em={email}&phn={phone}&id={update.message.from_user.id}')],
    ]))

    else:
      await update.message.reply_text(f"You haven't registered your Phone and Email. Register it from the Button below.\n",reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton(text='Register Details', url=f'https://somerandomlink.some/?data={update.message.from_user.id}')]]))

#####################modes#####################
async def show_chat_modes_handle(update: Update, context: CallbackContext):
  await update.message.reply_text("Here are available Chat Modes...")
  keyboard=[]
  for model in the_models:
    keyboard.append([InlineKeyboardButton(model, callback_data = f"set_chat_mode|{model}")])
  reply_markup = InlineKeyboardMarkup(keyboard)
  await update.message.reply_text("Select Chat Modes:", reply_markup=reply_markup)



#######################CallBack#####################
async def set_chat_mode_handle(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user.id

    query = update.callback_query
    await query.answer()

    chat_mode = query.data.split("|")[1]
    update_current_model(query.from_user.id,chat_mode)
    await query.edit_message_text(f"Hi {query.from_user.username}, I am {chat_mode}. What can i do for you?")



#########################new##################
async def new(update:Update,context:CallbackContext):
  await update.message.reply_text("Starting new dialog ✅")
  update_current_model(update.message.from_user.id,"Shriya (AI Assistant)")
  await update.message.reply_text("👩🏼‍🎓 Hi, I'm Shriya.Your AI Assistant. How can I help you?")
########################retry##################
async def retry(update:Update,context:CallbackContext):
  times_used=get_times_used(update.message.from_user.id)
  first_time =is_first_time_user(update.message.from_user.id)
  if not check_if_user_exists(update.message.from_user):
    create_new_user(update.message.from_user)
    await update.message.reply_text("Sorry can you ask again?")
  if not is_user_subscribed(update.message.from_user):
    await update.message.reply_text("Sorry, You are out of Subscription 🥹. \nto Subscribe use /subscribe command")
  elif first_time==True and times_used>50:
    await update.message.reply_text("Sorry, You have used your free trail./n Please Subscribe to continue. 🥹. \nTo Subscribe use /subscribe command")
    
  else:
    last_ques=get_last_question(update.message.from_user.id)
    model = fetch_current_model(update.message.from_user.id)
    await update.message.chat.send_action(action="typing")
    reply = ask_shriya(last_ques,update.message.from_user.id,model)
    reply=reply.choices[0].message.content
    await update.message.reply_text(reply)

#############################settings###################################
async def show_settings(update: Update, context: CallbackContext):
  await update.message.reply_text("Chat GPT is well Known Model. it's Fast and cheap. Ideal for everyday tasks. if there are some tasks it cant handle try GT-4. \n\nn🟢🟢🟢⚪️⚪️ -Smart\n🟢🟢🟢🟢🟢 -Fast\n🟢🟢🟢🟢🟢 -Cheap\n\n select model:")
  keyboard=[[InlineKeyboardButton("GPT-3.5", callback_data = f"set_settings|3.5")],[InlineKeyboardButton("GPT-4", callback_data = f"set_chat_mode|GPT_4")]]
  reply_markup = InlineKeyboardMarkup(keyboard)
  await update.message.reply_text("Select Chat Modes:", reply_markup=reply_markup)
########################voice_message_handle#####################
async def voice_message_handle(update: Update, context: CallbackContext):
  times_used=get_times_used(update.message.from_user.id)
  first_time =is_first_time_user(update.message.from_user.id)
  if not check_if_user_exists(update.message.from_user):
    create_new_user(update.message.from_user)
    await update.message.reply_text("Sorry can you ask again?")
  if not is_user_subscribed(update.message.from_user):
    await update.message.reply_text("Sorry, You are out of Subscription 🥹. \nto Subscribe use /subscribe command")
  elif first_time==True and times_used>50:
    await update.message.reply_text("Sorry, You have used your free trail./n Please Subscribe to continue. 🥹. \nTo Subscribe use /subscribe command")
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
    
    placeholder_message = await update.message.reply_text("...")

    # send typing action
    await update.message.chat.send_action(action="typing")
    update_message_text=transcribed_text
    
    entry_of_dialogs(update_message_text,update.message.id,"user",update_message_text)
    async def get_reply():
      model = fetch_current_model(update.message.from_user.id)
      reply = ask_shriya(transcribed_text,update.message.from_user.id,model)
      return reply
    reply= await get_reply()
    reply=reply.choices[0].message.content
    entry_of_dialogs(update.message.from_user.id,update.message.id,"bot",reply)
    await context.bot.edit_message_text(reply, chat_id=placeholder_message.chat_id, message_id=placeholder_message.message_id)
    
  

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
    application.add_handler(CommandHandler("modes", show_chat_modes_handle, filters=user_filter))
    application.add_handler(CommandHandler('profile', profile))
    application.add_handler(CommandHandler('subscribe', subscribe))
    application.add_handler(CommandHandler('retry', retry))
    application.add_handler(CommandHandler('settings', show_settings))
    application.add_handler(MessageHandler(filters.VOICE & user_filter, voice_message_handle))
    application.add_handler(CallbackQueryHandler(set_chat_mode_handle, pattern="^set_chat_mode"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, user_prompt))
    
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)
