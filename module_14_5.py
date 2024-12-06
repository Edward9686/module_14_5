from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from crud_functions import *
import asyncio

prod = get_all_products()

api = ''
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

kb = ReplyKeyboardMarkup(resize_keyboard=True)
kbi = InlineKeyboardMarkup()
kbi2 = InlineKeyboardMarkup(row_width=4, resize_keyboard=True)

buttoni = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='Калории')
buttoni1 = InlineKeyboardButton(text='Формулы рассчёта', callback_data='Формулы')

button = KeyboardButton(text='Информация!')
button2 = KeyboardButton(text='Расчитать...')
button3 = KeyboardButton(text='Купить!')
button4 = KeyboardButton(text='Регистрация!')


but1 = InlineKeyboardButton(text='Продукт 1', callback_data='product_buying')
but2 = InlineKeyboardButton(text='Продукт 2', callback_data='product_buying')
but3 = InlineKeyboardButton(text='Продукт 3', callback_data='product_buying')
but4 = InlineKeyboardButton(text='Продукт 4', callback_data='product_buying')

kb.add(button, button2, button3, button4)
kbi.add(buttoni, buttoni1)
kbi2.add(but1, but2, but3, but4)


@dp.message_handler(text='Купить')
async def handle_buy_button(message):
    await get_buying_list(message)


async def get_buying_list(message):
    product_info = f'Название: {prod[0][1]} | {prod[0][2]} | Цена: {prod[0][3]} руб.'
    with open('1.png', 'rb') as img:
        await message.answer_photo(img, product_info)
    product_info2 = f'Название: {prod[1][1]} | {prod[1][2]} | Цена: {prod[1][3]} руб.'
    with open('2.jpg', 'rb') as img2:
        await message.answer_photo(img2, product_info2)
    product_info3 = f'Название: {prod[2][1]} | {prod[2][2]} | Цена: {prod[2][3]} руб.'
    with open('3.jpg', 'rb') as img3:
        await message.answer_photo(img3, product_info3)
    product_info4 = f'Название: {prod[3][1]} | {prod[3][2]} | Цена: {prod[3][3]} руб.'
    with open('4.jpg', 'rb') as img4:
        await message.answer_photo(img4, product_info4)

    await message.answer('Выберите продукт для покупки:', reply_markup=kbi2)


@dp.callback_query_handler(text='product_buying')
async def send_confirm_message(call):
    await call.message.answer('Вы успешно приобрели продукт!')
    await call.answer()


@dp.message_handler(text='Расчитать')
async def main_menu(message):
    await message.answer('Выберите опцию:', reply_markup=kbi)


@dp.callback_query_handler(text='Формулы')
async def get_formulas(call):
    await call.message.answer('10 * вес(кг) + 6.25 * рост (см) – 4.92 * возраст – 161')
    await call.answer()


@dp.message_handler(commands=['start'])
async def start_message(message):
    await message.answer('Привет! Я бот помогающий твоему здоровью.', reply_markup=kb)


@dp.message_handler(text='Информация!')
async def button1(message):
    await message.answer('Привет! Я бот помогающий твоему здоровью.')


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


@dp.callback_query_handler(text='Калории')
async def set_age(call):
    await call.message.answer('Введите свой возраст(г):', reply_markup=kb)
    await call.answer()
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=int(message.text))
    await message.answer('Введите свой рост(см):')
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=int(message.text))
    await message.answer('Введите свой вес(кг):')
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight=int(message.text))
    data = await state.get_data()
    await message.answer(f'Ваша норма калорий: {10 * data["weight"] + 6.25 * data["growth"] - 5 * data["age"] - 161}')
    await state.finish()


class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()


@dp.message_handler(text='Регистрация!')
async def sign_up(message):
    await message.answer("Введите имя пользователя (только латинский алфавит):")
    await RegistrationState.username.set()


@dp.message_handler(state=RegistrationState.username)
async def set_username(message, state):
    username = message.text
    if is_included(username):
        await message.answer("Пользователь существует, введите другое имя:")
    else:
        await state.update_data(username=username)
        await message.answer("Введите свой email:")
        await RegistrationState.email.set()


@dp.message_handler(state=RegistrationState.email)
async def set_email(message, state):
    email = message.text
    await state.update_data(email=email)
    await message.answer("Введите свой возраст:")
    await RegistrationState.age.set()


@dp.message_handler(state=RegistrationState.age)
async def set_age(message, state):
    try:
        age = int(message.text)
        if age <= 0:
            raise ValueError("Возраст должен быть положительным.")
        data = await state.get_data()
        add_user(data['username'], data['email'], age)
        await message.answer("Регистрация завершена! Ваш баланс: 1000")
        await state.finish()
    except ValueError:
        await message.answer("Введите корректный возраст:")


@dp.message_handler()
async def all_message(message):
    await message.answer('Введите команду /start или нажмите кнопку "Информация!" чтобы начать общение.')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
