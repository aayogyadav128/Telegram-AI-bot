import pymongo
from pymongo import MongoClient
from datetime import datetime


uri = "mongodb+srv://Telegram-gpt-bot:vgryHahFQn7T0cZ3@cluster101.b01ps.mongodb.net/?retryWrites=true&w=majority"

# Create a new client and connect to the server
cluster = MongoClient(uri)


# Send a ping to confirm a successful connection
db = cluster["GptBot"]
collection = db["users"]
collection2 = db["dialogs"]


def check_if_user_exists(data):
  userid = data.id
  if collection.count_documents({"_id": userid})>0:
    return True
  else:
    return False
  # if collection.find({'_id': data.id}).count>0:
  #   return True
  # else:
  #   return False
  

def create_new_user(data):
  
  if not check_if_user_exists(data):
    user_dict = {
            "_id": data.id,

            "username": data.username,
            "first_name": data.first_name,
            "last_name": data.last_name,

            "last_interaction": datetime.now(),
            "first_seen": datetime.now(),

            "current_dialog_id": None,
            "current_chat_mode": "assistant",
            "current_model": "Shriya (AI Assistant)",
            "is_first_time": True,
            "n_used_tokens": {},

            "last_subscription_date": datetime.now() 
        }
    collection.insert_one(user_dict)





def check_days_left(data):
  userId = data.id
  sub_date = collection.find({"_id":userId})
  for sub in sub_date:
    lsd=sub["last_subscription_date"]
    lsd=lsd.date()
    date_now= datetime.now()
    date_now=date_now.date()
    delta=date_now-lsd
    delta_in_sec=delta.total_seconds()
    days_left=delta_in_sec/86400
    days_left=int(days_left)
    if days_left<30:
      days_left=30-days_left
      return days_left
    else:
      return 0

def get_times_used(id):
  dialog_data= collection2.find({"user_id":id,"sender":"user"})
  count=0
  for dialog in dialog_data:
    count+=1
  return count

def is_first_time_user(id):
  collection_data = collection.find({"_id":id})
  data={}
  for i in collection_data:
    data=i
  first_time = data["is_first_time"]
  if first_time:
    return True
  else:
    return False

def is_user_subscribed(data):
  left_days = check_days_left(data)
  if left_days<31:
    return True
  else:
    return False


def entry_of_dialogs(user_id,message_id,who,message):
  entry_dialog={"user_id": user_id,
                "message_id":message_id,
               "sender": who,
               "message": message,
               "datetime": datetime.now()}
  
  collection2.insert_one(entry_dialog)





def fetch_last_three_conversation(id):
  conversation=collection2.find({"user_id":id}).sort([( '$natural', -1 )]).limit(6)
  dict = []
  for conv in conversation:
    who=conv["sender"]
    mess=conv["message"]
    conv={who:mess}
    dict.append(conv)
  return dict
  print(dict)
  print(conversation)

def get_last_question(id):
  conversation=collection2.find({"user_id":id}).sort([( '$natural', -1 )]).limit(1)
  dict = {}
  for conv in conversation:
    dict=conv["message"]
  return dict


  
def check_if_has_phonenemail(userId):
  phone_email = collection.find({"_id":userId})
  dict=[]
  for i in phone_email:
    dict.append(i)
  if "phone_n_email" in dict[0]:
    return True
  else:
    return False
  
def get_phone_email(id):
  phone_email_ = collection.find({"_id":id})
  dict=[]
  for j in phone_email_:
    dict.append(j)
  data=dict[0]["phone_n_email"]
  
  return data

def set_phone_email(id,phone,email):
  collection.update_one({"_id": id},
    {"$set": {"phone_n_email": {"phone":phone,"email":email}}, "$currentDate": {"lastModified": True}},)
  

def update_current_model(id,current_model):
  collection.update_one({"_id": id},
    {"$set": {"current_model": current_model}, "$currentDate": {"lastModified": True}},)

def fetch_current_model(id):
  current_model = collection.find({"_id":id})
  current={}
  for curren in current_model:
    current=curren
  return current['current_model']

def check_if_first_time_n_over(id):
  times_used=get_times_used(id)
  first_time =if_first_time_user(id)
  if first_time==True and times_used>50:
    return True
    print("true")
  else:
    return False
    print("false")
