#import logging
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, BotCommand
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
import asyncio
import os
import traceback
from db_interaction import *

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
# Configure logging
#logging.basicConfig(level=logging.INFO)
# Initialize dispatcher
dp = Dispatcher()

class Form(StatesGroup):
    asking_food_amount = State()
    asking_other_amount = State()


async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Start the bot"),
        BotCommand(command="add_food_spending", description="Add food expense"),
        BotCommand(command="add_other_spending", description="Add other expense"),
        BotCommand(command="check_stats", description="Check spending statistics"),
    ]
    await bot.set_my_commands(commands)


@dp.message(CommandStart())
async def send_welcome(message: Message) -> None:
    await message.reply("I will help you track your food expenses")


@dp.message(Command("add_other_spending"))
async def ask_other_amount(message: Message, state: FSMContext) -> None:
    await message.reply(f"How much did you spend?")
    await state.set_state(Form.asking_other_amount)

@dp.message(Form.asking_other_amount)
async def add_other_spending(message: Message, state: FSMContext):
    amount = message.text  # Capture the user's name
    try:
        amount = f"{float(amount):.2f}"
        add_spending_DB(message.from_user.id, amount, "other")
        await message.answer(f"Added <b>{amount}</b> EUR")
        await state.clear()  # Clear the state after completing the flow
    except Exception as e:
        traceback.print_exc()
        await message.answer(f"Try again, enter only numbers with dot as separator!")
        await state.set_state(Form.asking_other_amount)


@dp.message(Command("add_food_spending"))
async def ask_food_amount(message: Message, state: FSMContext) -> None:
    await message.reply(f"How much did you spend?")
    await state.set_state(Form.asking_food_amount)


@dp.message(Form.asking_food_amount)
async def add_food_spending(message: Message, state: FSMContext):
    amount = message.text  # Capture the user's name
    try:
        amount = f"{float(amount):.2f}"
        add_spending_DB(message.from_user.id, amount, "food")
        await message.answer(f"Added <b>{amount}</b> EUR")
        await state.clear()  # Clear the state after completing the flow
    except Exception as e:
        traceback.print_exc()
        await message.answer(f"Try again, enter only numbers with dot as separator!")
        await state.set_state(Form.asking_food_amount)


@dp.message(Command("check_stats"))
async def send_welcome(message: Message) -> None:
    # Fetch user stats
    stats = get_user_spending_DB(message.from_user.id)

    # Helper function to format expenses
    def format_expenses(expenses):
        return '\n'.join(f"{key}: {value}" for key, value in expenses.items())

    # Format each category
    formatted_food = format_expenses(stats['food'])
    formatted_other = format_expenses(stats['other'])

    # Construct the message
    msg = (
    "🍽️ *Food Expenses* 🍴\n"
    f"{formatted_food}\n\n"
    "💼 *Other Expenses* 💳\n"
    f"{formatted_other}")

    await message.answer(msg, parse_mode="Markdown")



async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # Set the bot commands
    await set_bot_commands(bot)
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    #logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    is_test = int(os.getenv("IS_TEST"))
    if is_test:
        drop_tables_DB()
        create_tables_DB()
    asyncio.run(main())