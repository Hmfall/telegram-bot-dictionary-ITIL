from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from create_bot import dp, bot
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from database import sqlite_db
from keyboards import admin_kb
import os
from aiogram.types import ContentType
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


# Load
class FSMAdmin(StatesGroup):
    term = State()
    term_eng = State()
    definition = State()

ID = None


# Role
async def make_changes_command(message: types.Message):
    global ID
    ID = message.from_user.id
    await bot.send_message(message.from_user.id, "Role: Administrator", reply_markup=admin_kb.button_case_admin)


def is_admin(message):
    if message.from_user.id == ID:
        return True


async def cm_start(message: types.Message):
    if is_admin(message):
        await FSMAdmin.term.set()
        await message.reply("Enter the denomination of the term in Russian")


# cancel
async def cancel_load(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply("Download canceled")


async def load_term(message: types.Message, state: FSMContext):
    if is_admin(message):
        async with state.proxy() as data:
            data["term"] = message.text
            current_data = str(data["term"])
            if sqlite_db.is_value_uniqueness(current_data):
                await FSMAdmin.next()
                await message.reply("Enter the denomination of the term in English")
            else:
                await state.finish()
                await message.reply(f"<b>Error</b> \
                \nTerm <b>{current_data}</b> is currently in database \
                \nDownload canceled", parse_mode="HTML")


async def load_term_eng(message: types.Message, state: FSMContext):
    if is_admin(message):
        async with state.proxy() as data:
            data["term_eng"] = message.text
        await message.reply("Enter definition wording")
        await FSMAdmin.next()


async def load_definition(message: types.Message, state: FSMContext):
    if is_admin(message):
        async with state.proxy() as data:
            data["definition"] = message.text
        await sqlite_db.sql_add_command(state)
        async with state.proxy() as data:
            await message.reply("Loading is complete")
        await state.finish()


# import .xlsx
class FSMAdmin_load_excel(StatesGroup):
    load_xlsx = State()


async def load_xlsx_start(message: types.Message):
    if is_admin(message):
        await FSMAdmin_load_excel.load_xlsx.set()
        await message.reply("Download xlsx file")


@dp.message_handler(content_types=[ContentType.DOCUMENT], state=FSMAdmin_load_excel.load_xlsx)
async def load_term__y(message: types.Message, state: FSMContext):
    if is_admin(message):
        base_dir = os.path.dirname(os.path.abspath(__file__))

        if not os.path.exists(os.path.join(base_dir, "temp_uploads")):
            os.makedirs(os.path.join(base_dir, "temp_uploads"))

        file_name, file_ext = os.path.splitext(message.document.file_name)

        if file_ext != ".xlsx":
            await message.answer("The file must have an .xlsx extension")
            return

        file_path = os.path.join(base_dir, "temp_uploads", file_name + file_ext)

        if not os.path.isfile(file_path):
            await bot.download_file_by_id(message.document.file_id, file_path)

        try:
            count_added, count_skipped = sqlite_db.excel_initial(file_path)
            await message.reply(f"Records loaded: {count_added} \
            \nDuplicate entries skipped: {count_skipped}")
        except Exception as e:
            await message.reply(f"Error: {e}")

        os.remove(file_path)
        await state.finish()


# clear .db
class FSMAdmin_remove(StatesGroup):
    clear = State()


async def remove_start(message: types.Message):
    if is_admin(message): markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(KeyboardButton("Yes"), KeyboardButton("No"))
    await FSMAdmin_remove.clear.set()
    await message.reply("Confirm deletion of all dictionary entries", reply_markup=markup)


async def clear_all(message: types.Message, state: FSMContext):
    try:
        if is_admin(message):
            if message.text == "Yes":
                total = sqlite_db.clear_table()
                if total:
                    await bot.send_message(message.from_user.id, f"Deleted {total} records",
                                           reply_markup=admin_kb.button_case_admin)
                else:
                    await bot.send_message(message.from_user.id, "Error. The dictionary is empty. Deletion canceled",
                                           reply_markup=admin_kb.button_case_admin)
            else:
                await bot.send_message(message.from_user.id, "Deletion canceled",
                                       reply_markup=admin_kb.button_case_admin)
    except Exception as e:
        await bot.send_message(message.from_user.id, f"Error: {e}", reply_markup=admin_kb.button_case_admin)
    finally:
        await state.finish()


# export .xlsx
async def export_excel(message: types.Message):
    if is_admin(message):
        total_rows = sqlite_db.return_total_rows()
        if total_rows < 1:
            await message.reply("There are no records in the database to export")
        else:
            await bot.send_document(chat_id=message.chat.id,
                                    document=sqlite_db.export_excel_def(),
                                    caption=f"ITIL term database {sqlite_db.set_timestamp()} \
					\nTotal number of records: {total_rows}")


def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(cm_start, commands=[admin_kb.button_load_text])
    dp.register_message_handler(cancel_load, state="*", commands=admin_kb.button_cancel_text)
    dp.register_message_handler(cancel_load, Text(equals=admin_kb.button_cancel_text, ignore_case=True), state="*")
    dp.register_message_handler(load_term, state=FSMAdmin.term)
    dp.register_message_handler(load_term_eng, state=FSMAdmin.term_eng)
    dp.register_message_handler(load_definition, state=FSMAdmin.definition)
    dp.register_message_handler(remove_start, commands=[admin_kb.button_remove_all_text])
    dp.register_message_handler(clear_all, state=FSMAdmin_remove.clear)
    dp.register_message_handler(export_excel, commands=[admin_kb.button_export_excel_text])
    dp.register_message_handler(make_changes_command, commands=["moderator"], is_chat_admin=True)
    dp.register_message_handler(load_xlsx_start, commands=[admin_kb.button_import_excel_text])
