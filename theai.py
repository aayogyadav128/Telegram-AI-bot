import openai
import asyncio
from db import *
from models import *

openai.api_key = ""
class chatGpt:
  async def ask_shriya(question,id,model,dialog_messages):
  # get current model data
    actor=models.get(model)
  
    message=[]
    message.append({"role":"system", "content":actor})
    message+=dialog_messages
  
    
    message.append({"role": "user", "content": question})
    
    answer = None
    while answer is None:
      try:
        r_gen =await openai.ChatCompletion.acreate(
          model="gpt-3.5-turbo",
          messages=message,
          stream=True,
          temperature=0.7,
          frequency_penalty=0,
          max_tokens=1000,
          presence_penalty=0
        )
        answer = ""
        async for r_item in r_gen:
          delta = r_item.choices[0].delta
          if "content" in delta:
            answer += delta.content
            yield "not_finished",answer
      except openai.error.InvalidRequestError as e:
        # too many tokens
        if len(dialog_messages) == 0:
          raise e
    yield "finished", answer
  
async def transcribe_audio(audio_file):
      r = await openai.Audio.atranscribe("whisper-1", audio_file)
      return r["text"]
