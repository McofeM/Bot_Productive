
from aiogram import Bot, Dispatcher, F
import asyncio
import logging
from Bot_Productive.handlers.password import token
from aiogram.filters import CommandStart
from Bot_Productive.handlers.client import Form, Waiting
from Bot_Productive.handlers.other import updating_habits, reminder
from Bot_Productive.handlers.client import (get_start, button_text_handler, establish_habit, done_habits,
                                            inline_done_habits, execution_habit, number_performed, delete_button,
                                            delete_remember_time_waiting, remember_time, remember_time_waiting, delete_progres)
from aiogram.methods import DeleteWebhook

TOKEN = token


async def start_bot():
    print("БОТ ЗАПУЩЕН")


async def stop_bot():
    print("БОТ ВИМКНЕН")


async def start():
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - [%(levelname)s] - %(name)s - "
                               "(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s")
    bot = Bot(token=TOKEN)

    dp = Dispatcher()
    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)

    dp.message.register(get_start, CommandStart())
    dp.message.register(button_text_handler, lambda message: message.text in ["Встановити звичку", "Видалення", "⬅️ Повернутись назад", "⬅️ Повернутись назад ", "🏆 Прогрес"])
    dp.message.register(establish_habit, Form.waiting_establish_habit)
    dp.message.register(done_habits, F.text == "Позначити виконанні звички")
    dp.callback_query.register(inline_done_habits)
    dp.message.register(execution_habit, F.text == "Виконанні звички")
    dp.message.register(number_performed, F.text == "Прогрес по звичкам")
    dp.message.register(delete_button, F.text == "Видалити звичку")
    dp.message.register(delete_remember_time_waiting, F.text == "Видалити нагадування")
    dp.message.register(remember_time, F.text == "Встановити нагадування")
    dp.message.register(remember_time_waiting, Waiting.waiting_remember)
    dp.message.register(delete_progres, F.text == "Видалити прогрес")

    asyncio.create_task(reminder())
    asyncio.create_task(updating_habits())

    try:
        await bot(DeleteWebhook(drop_pending_updates=True))
        await dp.start_polling(bot)
    except asyncio.CancelledError:
        print("Асинхронні задачі були скасовані")
    except KeyboardInterrupt:
        print("Бот зупиняється...")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(start())
