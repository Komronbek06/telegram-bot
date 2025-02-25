import os
from aiogram import Bot, Dispatcher, types
import asyncio
from openai import OpenAI
from aiogram.filters import Command
import logging
from aiohttp import web

# Logging sozlamalari
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot tokeni va OpenAI API kaliti
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PORT = int(os.environ.get('PORT', 8080))

# OpenAI client yaratish
client = OpenAI(api_key=OPENAI_API_KEY)

# Bot va dispatcher yaratish
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Web app yaratish
app = web.Application()
routes = web.RouteTableDef()

@routes.get('/')
async def health_check(request):
    return web.Response(text='Bot ishlayapti!')

# /start buyrug'i
@dp.message(Command('start'))
async def start_command(message: types.Message):
    try:
        logger.info(f"Start command from user {message.from_user.id}")
        await message.reply("Assalomu alaykum! Men AI yordamchiman. Menga savolingizni yuboring.")
    except Exception as e:
        logger.error(f"Error in start command: {e}")

# Xabarlarni qayta ishlash
@dp.message()
async def handle_message(message: types.Message):
    if message.text is None:
        return
        
    try:
        logger.info(f"Received message from {message.from_user.id}: {message.text}")
        
        # OpenAI ga so'rov yuborish
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": message.text}
            ]
        )
        
        # Javobni olish va yuborish
        answer = response.choices[0].message.content
        logger.info(f"Sending response to {message.from_user.id}")
        await message.reply(answer)
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        await message.reply("Xatolik yuz berdi. Iltimos, keyinroq urinib ko'ring.")

async def start_bot():
    # Webhook ni o'chirish
    await bot.delete_webhook(drop_pending_updates=True)
    # Polling ni boshlash
    await dp.start_polling(bot, skip_updates=True)

def main():
    logger.info("Bot ishga tushmoqda...")
    app.add_routes(routes)
    
    # Bot va web server ni parallel ishga tushirish
    web.run_app(
        app,
        host='0.0.0.0',
        port=PORT,
        loop=asyncio.get_event_loop()
    )
    
    # Bot ni ishga tushirish
    asyncio.run(start_bot())

if __name__ == '__main__':
    main()
