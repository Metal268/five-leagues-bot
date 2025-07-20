import asyncio
import telegram
import feedparser
import os

# Налаштування
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '7578141836:AAGj_be7DOaq0wT-RL53gVDFEn_ZZMDNCXM')
CHAT_ID = os.getenv('CHAT_ID', '8142520596')
CHANNEL_ID = os.getenv('CHANNEL_ID', '@fiveleagues')  # Переконайся, що це правильний ID каналу

# RSS-стрічки для топ-5 ліг Європи
RSS_FEEDS = [
    'http://feeds.bbci.co.uk/sport/football/premier-league/rss.xml',  # АПЛ (Англія)
    'https://e00-marca.uecdn.es/rss/futbol/primera-division.xml',     # Ла Ліга (Іспанія)
    'https://www.gazzetta.it/rss/Xml/calcio.xml',                    # Серія А (Італія)
    'https://www.kicker.de/bundesliga/rss',                          # Бундесліга (Німеччина)
    'https://www.lequipe.fr/rss/football.xml'                        # Ліга 1 (Франція)
]

# Ініціалізація бота
bot = telegram.Bot(token=TELEGRAM_TOKEN)

# Ігнорування порту для Render
os.environ['PORT'] = '0'

async def fetch_news():
    news = []
    for feed in RSS_FEEDS:
        feed_data = feedparser.parse(feed)
        for entry in feed_data.entries[:1]:  # Беремо лише одну новину з кожної стрічки
            news.append({
                'title': entry.title,
                'summary': entry.summary,
                'link': entry.link
            })
    return news

async def format_final_post(news_item):
    # Готовий пост із журналістським стилем
    return f"""
🎙 *ОГЛЯД НОВИНИ З ТОП-5 ЛІГ* 🎙
*{news_item['title'].upper()}*

🔎 *Деталі:* {news_item['summary'][:250].replace('<p>', '').replace('</p>', '')}  
💡 *Коментар експерта:* Це може вплинути на боротьбу за чемпіонство! Що думаєте?  
🌐 [Читати повністю]({news_item['link']})

#АПЛ #ЛаЛіга #СеріяА #Бундесліга #Ліга1
"""

async def format_preview_post(news_item):
    # Попередній перегляд для затвердження
    comment = "👉 Перевір і затверди пост для @fiveleagues! Твоя думка? 👇"
    return f"""
📝 *ПЕРЕДПРОСМОТР ПОСТА* 📝
*{news_item['title'].upper()}*

🔎 {news_item['summary'][:150].replace('<p>', '').replace('</p>', '')}...  
🌐 [Джерело]({news_item['link']})
{comment}
💬 *Твоя дія:*
✅ Підтвердити | ❌ Відхилити | ✍️ Виправити
"""

async def send_news_to_user():
    news = await fetch_news()
    for item in news:
        preview_post = await format_preview_post(item)
        keyboard = [
            [{"text": "✅ Підтвердити", "callback_data": "confirm"},
             {"text": "❌ Відхилити", "callback_data": "decline"},
             {"text": "✍️ Виправити", "callback_data": "edit"}]
        ]
        reply_markup = telegram.InlineKeyboardMarkup(keyboard)
        message = await bot.send_message(chat_id=CHAT_ID, text=preview_post, reply_markup=reply_markup, parse_mode='Markdown')
        # Ручна обробка кнопок
        offset = 0
        while True:
            updates = await bot.get_updates(offset=offset, timeout=10)
            for update in updates:
                if update.callback_query and update.callback_query.message.message_id == message.message_id:
                    query = update.callback_query
                    await query.answer()
                    if query.data == "confirm":
                        final_post = await format_final_post(item)
                        await bot.send_message(chat_id=CHANNEL_ID, text=final_post, parse_mode='Markdown')
                        await query.edit_message_text("✅ Опубліковано в @fiveleagues!")
                    elif query.data == "decline":
                        await query.edit_message_text("❌ Відхилено.")
                    elif query.data == "edit":
                        await query.edit_message_text("✍️ Введи новий текст у відповіді.")
                    offset = update.update_id + 1
                    return  # Вихід після обробки
            await asyncio.sleep(1)  # Пауза, щоб не перевантажувати API

async def main():
    while True:
        await send_news_to_user()
        await asyncio.sleep(3600)  # Перевірка кожну годину

if __name__ == '__main__':
    asyncio.run(main())
