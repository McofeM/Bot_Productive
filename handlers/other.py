
from datetime import datetime, timedelta
import asyncio
import pymongo
from Bot_Productive.handlers.password import mangodbpassword
from aiogram import Bot
from Bot_Productive.handlers.password import token

mongo_client = pymongo.MongoClient(f"mongodb+srv://{mangodbpassword}@cluster0.inrqtd0.mongodb.net/")
db = mongo_client.Telegram_bot
collection = db["Bot_Productive"]
bot = Bot(token=token)


async def updating_habits():
    while True:
        now = datetime.now()
        midnight = datetime(now.year, now.month, now.day) + timedelta(days=1)
        time_to_midnight = (midnight - now).total_seconds()
        await asyncio.sleep(time_to_midnight)
        for doc_id in db.Bot_Productive.find():
            performance_habit = doc_id.get("performance_habit", [])
            if performance_habit:
                db.Bot_Productive.update_one(
                    {'_id': doc_id.get("_id", [])},
                    {'$push': {"unfulfilled_habits": {'$each': performance_habit}}}
                )
        db.Bot_Productive.update_many({}, {"$set": {"performance_habit": []}})


async def send_reminder(user_id):
    document = collection.find_one({"_id": user_id})
    if document["unfulfilled_habits"]:
        habits = '\n'.join(habit for habit in document["unfulfilled_habits"])
        await bot.send_message(chat_id=user_id, text=f"Тобі сьогодні ще потрібно зробити: \n{habits}")
    else:
        await bot.send_message(chat_id=user_id, text="Ти все зробив на сьогодні")


async def reminder():
    while True:
        try:
            documents = db.Bot_Productive.find()
            now_hour = datetime.now().strftime("%H:%M")
            for document in documents:
                if document["remember_time"]:
                    print("все працює")
                    for time in document["remember_time"]:
                        if time == now_hour:
                            print("все працює 2")
                            user_id = document["_id"]
                            await send_reminder(user_id)
        except Exception as e:
            print(f"Помилка: {e}")
        await asyncio.sleep(60)
