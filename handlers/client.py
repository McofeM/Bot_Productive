
from datetime import datetime
import pymongo
from Bot_Productive.handlers.password import mangodbpassword
from aiogram import Bot
from aiogram.types import Message, CallbackQuery
from Bot_Productive.handlers.reply import keyboard, create_keyboard, del_keyboard, del_keyboard_query, remember_keyboard, remember_time_keyboard, delete_progres_keyboard
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from random import choice
import re


mongo_client = pymongo.MongoClient(f"mongodb+srv://{mangodbpassword}@cluster0.inrqtd0.mongodb.net/")
db = mongo_client.Telegram_bot
collection = db["Bot_Productive"]

date = datetime.now().date()
formatted_date = date.strftime("%d-%m-%Y")


class Form(StatesGroup):
    waiting_establish_habit = State()


class Waiting(StatesGroup):
    waiting_remember = State()


async def add_user(user_id):
    if collection.find_one({"_id": user_id}):
        print(f"Користувач {user_id} вже існує в базі даних.")
    else:
        print(f"Додавання користувача {user_id} з датою {formatted_date} до бази даних.")
        result = collection.insert_one({
            "_id": user_id,
            "date": str(formatted_date),
            "unfulfilled_habits": [],
            "performance_habit": [],
            "number_performed": {},
            "remember_time": []
        })
        if result.acknowledged:
            print(f"Дані користувача {user_id} були успішно додані.")
        else:
            print(f"Помилка під час додавання даних користувачу {user_id}.")


# START
async def get_start(message: Message, bot: Bot):
    await bot.send_message(chat_id=message.from_user.id, text=f"Привіт {message.from_user.first_name}, я бот який допоможе тобі виробити корисні звички", reply_markup=keyboard)
    await add_user(message.from_user.id)


async def button_text_handler(message: Message, bot: Bot, state: FSMContext):
    if message.text == "Встановити звичку":
        await state.clear()
        await state.set_state(Form.waiting_establish_habit)
        await bot.send_message(chat_id=message.from_user.id, text="Ведіть свою звичку, для того щоб скасувати вод даних натисність на кнопку 'Відмінити команду'")
    elif message.text == "Видалення":
        await bot.send_message(chat_id=message.from_user.id, text="❌ Ви обрали видалення", reply_markup=del_keyboard)
    elif message.text == "⬅️ Повернутись назад":
        await bot.send_message(chat_id=message.from_user.id, text="Ви повернулись назад", reply_markup=keyboard)
    elif message.text == "🏆 Прогрес":
        await bot.send_message(chat_id=message.from_user.id, text="🏆 Ви обрали вкладку прогрес", reply_markup=remember_keyboard)
    elif message.text == "⬅️ Повернутись назад ":
        await bot.send_message(chat_id=message.from_user.id, text="Ви повернулись назад", reply_markup=keyboard)
    else:
        await bot.send_message(chat_id=message.from_user.id, text="Я вас не розумію")


async def establish_habit(message: Message, bot: Bot, state: FSMContext):
    if message.text == "Відмінити команду":
        await state.clear()
        await bot.send_message(chat_id=message.from_user.id, text="Ви скасували вод даних")
    elif collection.find_one({"_id": message.chat.id}):
        collection.update_one(
            {"_id": message.chat.id},
            {"$push": {"unfulfilled_habits": message.text}}
        )
        await bot.send_message(chat_id=message.from_user.id, text="Ваша звичка записанна ")
    else:
        await bot.send_message(chat_id=message.from_user.id, text="Чомусь вас нема у базі, будь ласко натисніть кнопку start")


async def done_habits(message: Message, bot: Bot):
    if collection.find_one({"_id": message.from_user.id}):
        document = collection.find_one({"_id": message.from_user.id})
        if not document["unfulfilled_habits"]:
            await bot.send_message(chat_id=message.from_user.id,
                                   text="Ви ще не вписали звички, натисніть на кнопку 'Встановити звичку'")
        else:
            await bot.send_message(chat_id=message.from_user.id,
                                   text="Які цілі ви сьогодні виконали?", reply_markup=await create_keyboard(document["unfulfilled_habits"])
                                   )
    else:
        await bot.send_message(chat_id=message.from_user.id, text="Чомусь вас нема у базі, будь ласко натисніть кнопку start")


async def execution_habit(message: Message, bot: Bot):
    document = collection.find_one({"_id": message.from_user.id})
    performance_habit = document["performance_habit"]
    tasks_formatted = '\n'.join(performance_habit)
    await bot.send_message(chat_id=message.from_user.id, text=f"✅ Ти виконав {len(performance_habit)} завдань:\n{tasks_formatted}")


async def number_performed(message: Message, bot: Bot):
    document = collection.find_one({"_id": message.from_user.id})
    if document["number_performed"]:
        number = document["number_performed"]
        try:
            output = "\n".join([f"{key}: {value}" for key, value in number.items()])
            await bot.send_message(chat_id=message.from_user.id, text=output)
        except AttributeError:
            await bot.send_message(chat_id=message.from_user.id, text="Ви ще ні чого не виконали")
    else:
        await bot.send_message(chat_id=message.from_user.id, text="У вас нема виконаних завдань, щоб вони з'явились, "
                                                                  "перейдіть у вкладку 'Позначити виконанні звички'")


async def delete_button(message: Message, bot: Bot, state: FSMContext):
    await state.clear()
    document = collection.find_one({"_id": message.from_user.id})
    if not document["unfulfilled_habits"] or not ["performance_habit"]:
        await bot.send_message(chat_id=message.from_user.id,
                               text="Ви ще не вписали звички, натисніть на кнопку 'Встановити звичку'")

    else:
        all_document = document["unfulfilled_habits"] + document["performance_habit"]
        await bot.send_message(chat_id=message.from_user.id,
                               text="Оберіть звичку для видалення", reply_markup=await del_keyboard_query(all_document)
                               )


async def inline_done_habits(callback_query: CallbackQuery):
    await callback_query.bot.answer_callback_query(callback_query.id)
    if callback_query.data.startswith("executed"):
        # додаємо користувача до "performance_habit"
        collection.update_one(
            {"_id": callback_query.message.chat.id},
            {"$push": {"performance_habit": callback_query.data[9:]}}
        )
        # Рахує скільки раз ви виконали звичку
        collection.update_one(
            {"_id": callback_query.message.chat.id},
            {"$inc": {f"number_performed.{callback_query.data[9:]}": 1}}
        )
        # видаляємо користувача з "unfulfilled_habits"
        collection.update_one(
            {"_id": callback_query.message.chat.id},
            {"$pull": {"unfulfilled_habits": callback_query.data[9:]}}
        )
        document = collection.find_one({"_id": callback_query.message.chat.id})
        if not document["unfulfilled_habits"]:
            praise = ["Ого, ти все виконав",
                      "Ти виконав всі свої звички, продовжуй в тому ж дусі",
                      "Ой йой йой, який ти крути ти виконав всі свої плани",
                      "Який ти крутий, ти все виконав",
                      "Тепер можеш відпочити, ти все виконав"
                      ]
            await callback_query.bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                                       message_id=callback_query.message.message_id,
                                                       text=choice(praise)
                                                       )
        else:
            await callback_query.bot.send_message(chat_id=callback_query.message.chat.id,
                                                  text=f"✅ Ви виконали  {callback_query.data[9:]}"
                                                  )
            await callback_query.bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                                       message_id=callback_query.message.message_id,
                                                       text="Позначте цілі які ви виконали",
                                                       reply_markup=await create_keyboard(document["unfulfilled_habits"])
                                                       )
    elif callback_query.data.startswith("del"):
        habit_to_delete = callback_query.data[4:]
        updated = False

        for field in ["unfulfilled_habits", "performance_habit"]:
            if collection.find_one({field: habit_to_delete, "_id": callback_query.message.chat.id}):
                collection.update_one(
                    {"_id": callback_query.message.chat.id},
                    {"$pull": {field: habit_to_delete}}
                )
                updated = True
                break
        if updated:
            document = collection.find_one({"_id": callback_query.message.chat.id})
            all_document = document["unfulfilled_habits"] + document["performance_habit"]
            await callback_query.bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                                       message_id=callback_query.message.message_id,
                                                       text="Позначте цілі які потрібно видалити",
                                                       reply_markup=await del_keyboard_query(all_document)
                                                       )
            await callback_query.bot.send_message(chat_id=callback_query.message.chat.id,
                                                  text=f"❌ Ви видалили звичку {habit_to_delete}"
                                                  )
        else:
            await callback_query.bot.send_message(chat_id=callback_query.message.chat.id,
                                                  text="Більше нічого видаляти")
    elif callback_query.data.startswith("rem"):
        collection.update_one(
            {"_id": callback_query.message.chat.id},
            {"$pull": {"remember_time": callback_query.data[4:]}}
        )
        await callback_query.bot.send_message(chat_id=callback_query.message.chat.id,
                                              text=f"Ви видалили: {callback_query.data[4:]}"
                                              )
        document = collection.find_one({"_id": callback_query.message.chat.id})
        if not document["remember_time"]:
            await callback_query.bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                                       message_id=callback_query.message.message_id,
                                                       text="Ти вже все видалив")
        else:
            await callback_query.bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                                       message_id=callback_query.message.message_id,
                                                       text="Яке ще нагадування ви хочете видалити",
                                                       reply_markup=await remember_time_keyboard(document["remember_time"])
                                                       )
    elif callback_query.data.startswith("prog"):
        collection.update_one(
            {"_id": 873674161},
            {"$unset": {f"number_performed.{callback_query.data[5:]}": ""}}
        )
        await callback_query.bot.send_message(chat_id=callback_query.message.chat.id,
                                              text=f"Ти видалив {callback_query.data[5:]}")
        document = collection.find_one({"_id": callback_query.message.chat.id})
        if not document["number_performed"]:
            await callback_query.bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                                       message_id=callback_query.message.message_id,
                                                       text="Ти вже все видалив")
        else:
            await callback_query.bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                                       message_id=callback_query.message.message_id,
                                                       text="Який ще прогрес ти хочеш видалити",
                                                       reply_markup=await delete_progres_keyboard(document["remember_time"])
                                                       )
    else:
        await callback_query.bot.send_message(chat_id=callback_query.message.chat.id, text="Щось пішло не так")


async def remember_time(message: Message, bot: Bot, state: FSMContext):
    await state.set_state(Waiting.waiting_remember)
    await bot.send_message(chat_id=message.from_user.id, text="Ведіть час коли вам нагадувати про завдання у форматі години:хвилини")


async def remember_time_waiting(message: Message, bot: Bot, state: FSMContext):
    time_pattern = re.compile(r"^([01]?\d|2[0-3]):([0-5]\d)$")
    if time_pattern.match(message.text):
        await bot.send_message(chat_id=message.from_user.id, text=f"Встановлений час нагадування, {message.text}")
        collection.update_one(
            {"_id": message.from_user.id},
            {"$push": {"remember_time": message.text}}
        )
    elif message.text == "Відмінити команду":
        await state.clear()
        await bot.send_message(chat_id=message.from_user.id, text="Ви скасували вод даних")
    else:
        await bot.send_message(chat_id=message.from_user.id, text=f"Ви обрали неправильний формат")


async def delete_remember_time_waiting(message: Message, bot: Bot, state: FSMContext):
    document = collection.find_one({"_id": message.from_user.id})
    if document["remember_time"]:
        await bot.send_message(chat_id=message.from_user.id, text="Яке нагадування ви хочете видалити?",
                               reply_markup=await remember_time_keyboard(document["remember_time"]))
    else:
        await bot.send_message(chat_id=message.from_user.id, text="У вас нема встановленого нагадування часу")
        await state.clear()


async def delete_progres(message: Message, bot: Bot):
    document = collection.find_one({"_id": message.from_user.id})
    if document["number_performed"]:
        await bot.send_message(chat_id=message.from_user.id, text="Який прогрес завдань ви хочете видалити?",
                               reply_markup=await delete_progres_keyboard(document["number_performed"]))
    else:
        await bot.send_message(chat_id=message.from_user.id, text="У вас нема виконаних завдань, щоб вони з'явились, "
                                                                  "перейдіть у вкладку 'Позначити виконанні звички'")
