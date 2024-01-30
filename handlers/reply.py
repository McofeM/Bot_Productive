from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Кнопка для скасування машиного стану
cancel_status_button = KeyboardButton(text="Відмінити команду")

button1 = KeyboardButton(text="Встановити звичку")
button2 = KeyboardButton(text="Позначити виконанні звички")
button3 = KeyboardButton(text="Виконанні звички")
button4 = KeyboardButton(text="🏆 Прогрес")
button5 = KeyboardButton(text="Видалення")
keyboard_buttons = [[button1, button2, button3], [button4, button5], [cancel_status_button]]

keyboard = ReplyKeyboardMarkup(keyboard=keyboard_buttons, resize_keyboard=True)


# Створення клавіатури для виконаних дій
async def create_keyboard(buttons):
    keyboard_layout = [[InlineKeyboardButton(text=button, callback_data="executed_"+button)] for button in buttons]
    done_habits_keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_layout)
    return done_habits_keyboard


# Створення клавіатури для видалення
async def del_keyboard_query(buttons):
    keyboard_del_layout = [[InlineKeyboardButton(text=button, callback_data="del_"+button)] for button in buttons]
    done_habits_del_keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_del_layout)
    return done_habits_del_keyboard


# Видалення нагадувань
async def remember_time_keyboard(buttons):
    remember_time_button = [[InlineKeyboardButton(text=button, callback_data="rem_"+button)] for button in buttons]
    remember_time = InlineKeyboardMarkup(inline_keyboard=remember_time_button)
    return remember_time


# Видалення прогресу
async def delete_progres_keyboard(buttons):
    progres_button = [[InlineKeyboardButton(text=button, callback_data="prog_"+button)] for button in buttons]
    delete_progres_buttons = InlineKeyboardMarkup(inline_keyboard=progres_button)
    return delete_progres_buttons


# Кнопки для видалення кнопок
del_button1 = KeyboardButton(text="Видалити звичку")
del_button2 = KeyboardButton(text="Видалити прогрес")
del_button3 = KeyboardButton(text="Видалити нагадування")
back_button = KeyboardButton(text="⬅️ Повернутись назад")

del_keyboard_buttons = [[del_button1, del_button2, del_button3], [back_button]]

del_keyboard = ReplyKeyboardMarkup(keyboard=del_keyboard_buttons, resize_keyboard=True)

# Кнопки клавіатури прогрес

remember_button1 = KeyboardButton(text="Прогрес по звичкам")
remember_button2 = KeyboardButton(text="Встановити нагадування")
remember_button3 = KeyboardButton(text="⬅️ Повернутись назад ")
remember_keyboard_buttons = [[remember_button1,  remember_button2, remember_button3], [cancel_status_button]]

remember_keyboard = ReplyKeyboardMarkup(keyboard=remember_keyboard_buttons, resize_keyboard=True)
