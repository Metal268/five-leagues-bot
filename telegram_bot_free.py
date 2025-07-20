import asyncio
import telegram
import feedparser
import os

# Налаштування
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '7578141836:AAGj_be7DOaq0wT-RL53gVDFEn_ZZMDNCXM')
CHAT_ID = os.getenv('CHAT_ID', '8142520596')
CHANNEL_ID = os.getenv('CHANNEL_ID', 'fiveleagues')

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

async def format_post(news_item):
    comment = "👉 Журналістський вайб: Гучна новина для фанатів? Твоя думка? 👇"
    return f"""
🔥 *{news_item['title'].upper()}* 🔥
{news_item['summary'][:250]}...
🌐 [Докладніше]({news_item['link']})
{comment}
💬 *Твоя дія:*
✅ Підтвердити | ❌ Відхилити | ✍️ Виправити
"""

async def send_news_to_user():
    news = await fetch_news()
    for item in news:
        post = await format_post(item)
        keyboard = [
            [{"text": "✅ Підтвердити", "callback_data": "confirm"},
             {"text": "❌ Відхилити", "callback_data": "decline"},
             {"text": "✍️ Виправити", "callback_data": "edit"}]
        ]
        reply_markup = telegram.InlineKeyboardMarkup(keyboard)
        message = await bot.send_message(chat_id=CHAT_ID, text=post, reply_markup=reply_markup, parse_mode='Markdown')
        # Обробка кнопок
        while True:
            update = await bot.get_updates(timeout=10)
            for u in update:
                if u.callback_query and u.callback_query.message.message_id == message.message_id:
                    query = u.callback_query
                    await query.answer()
                    if query.data == "confirm":
                        await query.edit_message_text("✅ Опубліковано в @fiveleagues! (Поки тест)")
                    elif query.data == "decline":
                        await query.edit_message_text("❌ Відхилено.")
                    elif query.data == "edit":
                        await query.edit_message_text("✍️ Введи новий текст у відповіді.")
                    return  # Вихід із циклу після обробки

async def main():
    while True:
        await send_news_to_user()
        await asyncio.sleep(3600)  # Перевірка кожну годину

if __name__ == '__main__':
    asyncio.run(main())
