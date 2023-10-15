from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


button_load_text = "Load"
button_cancel_text = "Cancel"
button_export_excel_text = "Export"
button_import_excel_text = "Import"
button_remove_all_text = "Remove"


button_load = KeyboardButton(f"/{button_load_text}")
button_cancel = KeyboardButton(f"/{button_cancel_text}")
button_export_excel = KeyboardButton(f"/{button_export_excel_text}")
button_import_excel = KeyboardButton(f"/{button_import_excel_text}")
button_remove_all = KeyboardButton(f"/{button_remove_all_text}")


button_case_admin = ReplyKeyboardMarkup(resize_keyboard=True) \
	.row(button_load, button_import_excel) \
	.add(button_cancel) \
	.add(button_export_excel) \
	.add(button_remove_all)