import openai
from db import *



openai.api_key = ""

models={"Shriya (AI Assistant)":"An Ai Assistant Named Shriya",
       "Code Assitant":"A code Assitant",
       "Startup Idea Generator":"Startup Idea Generator bot",
       "Relationship coach":"A Relationship Coach named Jeetu",
       "CV Builder":"CV Builder Robot",
       "Teacher":"Teacher named alakh",
       "A.P.J Abdul Kalam":"Indian Scientist, Dr. A.P.J Abdul Kalam",
       "Albert Einstien":"Albert Einstien",
       "Sandeep Maheshwari":"Motivational Speaker named Sandeep Maheshwari",
       "Narendra Modi":"Prime Minister of India, Narendra Modi"}

def ask_shriya(question,id,model):
  actor=models.get(model)  
  dialog_messages=fetch_last_three_conversation(id)
  message=[]
  message.append({"role": "system", "content": f"you are {actor}"})
  for dialog_message in dialog_messages:
    if 'user' in dialog_message:
      message.append({"role": "user", "content": dialog_message["user"]})
    else:
      message.append({"role": "assistant", "content": dialog_message["bot"]})
  message.append({"role": "user", "content": question})
  response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=message,
    temperature=0.7,
    frequency_penalty=0,
    max_tokens=1000,
    presence_penalty=0
  )
  return response

async def transcribe_audio(audio_file):
    r = await openai.Audio.atranscribe("whisper-1", audio_file)
    return r["text"]
  
