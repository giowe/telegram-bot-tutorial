from time import sleep
import json

import requests

f = open("token.txt")
token = f.read()
f.close()

api_url = "https://api.telegram.org/bot" + token + "/"

def get_updates(offset):
  r = requests.post(api_url + "getUpdates", json={ "offset": offset })
  data = r.json()
  updates = data["result"]
  return updates

def send_message(chat_id, text):
  requests.post(api_url + "sendMessage", json={
    "chat_id": chat_id,
    "text": text 
  })

def reply(message, text):
  send_message(message["chat"]["id"], text)

def handle_message(message):
  if "text" in message:
    text = message["text"]

    if text[0] == "/":
      splitted_text = text.split(" ")
      command = splitted_text.pop(0)
      text = " ".join(splitted_text)

      if command == "/parrot":
        parrot(message, text)
      elif command == "/btc":
        btc(message, text)

  elif "new_chat_members" in message:
    new_member_names = []
    for member in message["new_chat_members"]:
      new_member_names.append(member["first_name"])
    
    new_member_count = len(new_member_names)
    if new_member_count == 1:
      reply(message, "Benvenuto " + new_member_names[0])
    elif new_member_count == 2:
      reply(message, "Benvenuti ", " e ".join(new_member_names))
    else:
      reply(message, "Benvenuti ", ", ".join(new_member_names))

  elif "left_chat_member" in message:
    reply(message, "Bye bye " + message["left_chat_member"]["first_name"])

def parrot(message, text):
  reply(message, message["from"]["first_name"] + " ha scritto \"" + text + "\"")

def btc(message, text):
  r = requests.get("https://blockchain.info/ticker")
  data = r.json()

  currency = text.upper()
  if text == "" or currency not in data:
    reply(message, "Devi specificare in quale delle seguenti valute ti interessa conoscere il valore di 1 Bitcoin:\n" + ", ".join(data.keys()))
  else:
    reply(message, "1 Bitcoin = " + str(data[currency]["last"]) + " " + currency)

offset = 0
while True:
  updates = get_updates(offset)
  print(json.dumps(updates, indent=2))

  if len(updates) > 0:
    offset = updates[-1]["update_id"] + 1
    for update in updates:
      handle_message(update["message"])

  sleep(1)