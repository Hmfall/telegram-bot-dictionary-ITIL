from aiogram import types, Dispatcher
from create_bot import dp, bot
from aiogram.types import ReplyKeyboardRemove


async def command_start(message : types.Message):
	try: 
		await bot.send_message(message.from_user.id, 
			 "<b>Launched</b> \
			 \nTo search for a term, enter: \
			 \n<b>@DictionaryITILbot</b> *denomination*",
			 parse_mode='HTML', reply_markup=ReplyKeyboardRemove())
		await message.delete()
	except:
		await message.reply("DictionaryITILbot: \nhttps://t.me/DictionaryITILbot")


def register_handlers_client(dp : Dispatcher):
	dp.register_message_handler(command_start, commands=["start", "help"])

