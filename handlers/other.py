from aiogram import types, Dispatcher
import os, json, string
from create_bot import dp


path_cenz_json = "\cenz\cenz.json"


async def cenz(message : types.Message):
	if {i.lower().translate(str.maketrans("", "", string.punctuation))\
	for i in message.text.split(" ")}\
		.intersection(set(json.load(open(\
      os.path.dirname(os.path.abspath(__file__)) + path_cenz_json)))) != set():
		await message.reply("Message defined as forbidden")
		await message.delete()


def register_handlers_other(dp : Dispatcher):
	dp.register_message_handler(cenz)

