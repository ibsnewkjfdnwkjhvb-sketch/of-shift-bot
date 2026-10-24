import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_CHAT_ID = 123456789  # ⚠️ Напишите сюда ваш Telegram ID

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class ShiftForm(StatesGroup):
    waiting_for_report = State()

def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("🟢 Начал работу"))
    keyboard.add(KeyboardButton("🔴 Завершил работу"))
    return keyboard

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer("Привет! Используй кнопки ниже для управления сменой.", reply_markup=get_main_keyboard())

@dp.message_handler(lambda msg: msg.text == "🟢 Начал работу")
async def start_shift(message: types.Message):
    await message.answer("Принято! Пожалуйста, напиши данные за прошлый день:\n\n1. Сколько пришло фанов?\n2. Сколько заработано ($)?")
    await ShiftForm.waiting_for_report.set()

@dp.message_handler(state=ShiftForm.waiting_for_report)
async def process_report(message: types.Message, state: FSMContext):
    user_report = message.text
    user_name = message.from_user.full_name
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    await message.answer("Смена успешно начата! Хорошей работы.", reply_markup=get_main_keyboard())
    await state.finish()
    
    notification = (
        f"🟢 **ПОМОЩНИК ЗАШЕЛ НА СМЕНУ**\n"
        f"👤 Помощник: {user_name}\n"
        f"⏰ Время: {current_time}\n\n"
        f"📊 **Отчет за прошлый день:**\n{user_report}"
    )
    await bot.send_message(chat_id=OWNER_CHAT_ID, text=notification, parse_mode="Markdown")

@dp.message_handler(lambda msg: msg.text == "🔴 Завершил работу")
async def end_shift(message: types.Message):
    user_name = message.from_user.full_name
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    await message.answer("Смена завершена! Отдыхай.", reply_markup=get_main_keyboard())
    
    notification = (
        f"🔴 **ПОМОЩНИК ВЫШЕЛ СО СМЕНЫ**\n"
        f"👤 Помощник: {user_name}\n"
        f"⏰ Время: {current_time}"
    )
    await bot.send_message(chat_id=OWNER_CHAT_ID, text=notification, parse_mode="Markdown")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)