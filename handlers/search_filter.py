import sqlite3
from aiogram import types
from create_bot import dp, bot
from database import sqlite_db
import hashlib


def search_terms(query, limit = 10, offset = 1):
   try:
      articles = []
      if query.strip() and len(query.strip()) >= offset:
         conn = sqlite3.connect(sqlite_db.database_name())
         cursor = conn.cursor()
         cursor.execute(f"SELECT \
                     	term, term_eng, definition FROM {sqlite_db.dictionary_table_name()} \
								WHERE term LIKE ? \
								LIMIT ? OFFSET ?", (query+'%', limit, offset))
         results = cursor.fetchall()
         for result in results:
               article = types.InlineQueryResultArticle(
					id = hashlib.sha1(result[0].encode('utf-8')).hexdigest(), 
					title = result[0],
					description = f"{result[1]}\n{result[2]}",
					input_message_content=types.InputTextMessageContent(
					message_text=f"<b>{result[0]}</b>\n<b>{result[1]}</b>\n{result[2]}", parse_mode='HTML')
					)
               articles.append(article)
         cursor.close()
         conn.close()
   except Exception as e:
          print(e)
   return articles


@dp.inline_handler()
async def inline_search(query: types.InlineQuery):
   search_query = query.query
   next_offset = int(query.offset) + 10 if query.offset else 10
   results = search_terms(search_query, offset=int(query.offset or 0))
   if len(results) == 10:
      await bot.answer_inline_query(query.id, results=results, next_offset=str(next_offset))
   else:
      await bot.answer_inline_query(query.id, results=results)
   