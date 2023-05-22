from aiogram import executor, Bot, types, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

import pymysql

conn = pymysql.connect(
    host='mysqlserver3.mysql.database.azure.com',
    user='yehor',
    password='4vRes4^9mH',
    database='messenger'
)
cursor = conn.cursor()


member_info = []

token = "5955853716:AAGo4_fpcPMjZ99D0jOCEoxAPC4ImEa3TIo"
bot = Bot(token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands=['start'])
async def start(message: types.Message, state: FSMContext):
    print(message.from_user.username+": "+ message.text)
    await state.set_state('waiting_for_login')
    await message.answer(text = "hello")
    await message.answer(text="Здравейте\nВведите свой логин:")

@dp.message_handler(content_types=[types.ContentType.NEW_CHAT_MEMBERS])
async def user_joined_chat(message: types.Message, state: FSMContext):
    print(f'User {message.from_user.username} added')
    await state.set_state('waiting_for_login')
    await message.answer(text="Здравейте\nВведите свой логин:")

@dp.message_handler(content_types = [types.ContentType.TEXT], state = "waiting_for_login")
async def login_input(message: types.Message, state: FSMContext):
    print(message.from_user.username+": "+ message.text)
    cursor.execute("SELECT * FROM chats_users WHERE email = %s",(message.text,))
    if cursor.fetchall():
        member_info.append(message.text)
        await state.set_state('waiting_for_password')
        await message.answer(text="Введите пароль:")
    else:
        await state.set_state('waiting_for_login')
        await message.answer(text="Такого пользователя не существует\nВведите логин еще раз:")


@dp.message_handler(content_types = [types.ContentType.TEXT], state = "waiting_for_password")
async def password_input(message: types.Message, state: FSMContext):
    print(message.from_user.username+": "+ message.text)
    cursor.execute("SELECT * FROM chats_users WHERE email = %s AND password = %s",(member_info[0], message.text,))
    if cursor.fetchall():
        member_info.append(message.text)
        await state.finish()
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(text="садись прокачу", url="https://www.youtube.com/watch?v=nx3A-YmfFHw&ab_channel=%D0%91%D0%B0%D0%BB%D0%B1%D0%B5%D1%81%D1%8B"))
        await message.answer(text="Вы прошли проверку на пидора, подздравляем!", reply_markup=markup)
    else:
        await state.set_state('waiting_for_password')
        await message.answer(text="Вы ввели неверный пароль, попробуйте еще раз:")




if __name__ == "__main__":
    try:
        executor.start_polling(dp, skip_updates=True)
    finally:
        # Закрытие соединения с базой данных
        conn.close()