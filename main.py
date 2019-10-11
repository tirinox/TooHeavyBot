from src.util.config import Config
from aiotg import Bot, Chat


bot = Bot(api_token=Config().get('telegram.token'))


@bot.command(r"hi")
async def test_hi(chat: Chat, match):
    await chat.send_text('hi!')


if __name__ == "__main__":
    bot.run(debug=Config().is_debug)