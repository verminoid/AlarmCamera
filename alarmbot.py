import telebot
from dvrip import DVRIPCam #from NeiroN
import secret
from alarmdatabase import DataBaseBot

DATABASE = 'data.db'

base = DataBaseBot(DATABASE)
bot = telebot.TeleBot(secret.TOKEN)

def extract_arg(arg):
    """извлечение аргументов"""
    return arg.split()[1:]


def extract_1_arg(arg):
    """извлечение длинного аргумента"""
    return arg.split(maxsplit=1)[1:]

@bot.message_handler(commands=['start'])
def start_handler(message):
    """ start проверяет пароль"""
    qstart = extract_arg(message.text)
    if message.from_user.id in base.list_users():
        bot.send_message(message.chat.id,
                        f"{message.from_user.first_name}, Я уже вас видел, для помощи - /help")
    else:
        if len(qstart):
            if qstart[0] == str(secret.BOT_PASS):
                base.new_user(
                    message.from_user.id, message.from_user.username, message.from_user.first_name, subs=True)
                bot.send_message(
                    message.chat.id,
                    f"Я вас запомнил, {message.from_user.first_name}!\nВы автоматически подписаны на тревожные оповещения\nЧтобы узнать, что я могу, введите /help ")
                
            else:
                bot.reply_to(message, "кодовая фраза не верна")
        else:
            bot.send_message(message.chat.id, f"{message.from_user.first_name}, Вы не туда попали!")
        