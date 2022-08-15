import telebot
from dvrip import DVRIPCam #from NeiroNx
import secret
from alarmdatabase import DataBaseBot

DATABASE = 'data.db'

base = DataBaseBot(DATABASE)
bot = telebot.TeleBot(secret.TOKEN)

cams = {}
for cloud_id, address, name, user, password in base.cams_list():
    cam = DVRIPCam(address, user=user, password=password)
    if cam.login():
        cam.close()
        cams.update({name: cam})

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


@bot.message_handler(commands=['snapshot'], func=lambda message: base.user_exists(message.from_user.id))
def get_snapshot(message):
    """get snapshot from all camera

    """    
    for name, cam in cams.items():
        if cam.login():
            try:
                snap = cam.snapshot()
                bot.send_photo(message.from_user.id, snap, caption=name)
            except:
                bot.send_message(message.chat.id, f'Не удалось получить картинку с камеры {name}. IP: {address}. CloudId: {cloud_id}')
            cam.close()
        else:
            bot.send_message(message.chat.id, f'Не удалось  подключиться к камере {name}. IP: {address}.     CloudId: {cloud_id}')
        

@bot.message_handler(commands=['new_cam'], func=lambda message: base.user_exists(message.from_user.id))
def new_cam(message):
    """create new db entry of camera"""
    n_cam = extract_arg(message.text)
    if len(n_cam)>=2:
        cam = DVRIPCam(n_cam[0], user=n_cam[1], password=n_cam[2])
        if cam.login():
            name = cam.get_info("ChannelTitle")[0]
            cloud_id = cam.get_system_info()['SerialNo']
            cam.close()
            base.new_cam(cloud_id=cloud_id, address=n_cam[0],   name=name, user=n_cam[1], password=n_cam[2])
            cams.update({name: cam})
        else:
            bot.send_message(message.chat.id, 'Не удалось подключиться к камере с данными параметрами')
    else:
        bot.send_message(message.chat.id, 'Введите имя пользователя и пароль')

@bot.message_handler(commands=['Alarm'], func=lambda message: base.user_exists(message.from_user.id))
def alarm_on_off(message):
    """On/off Motion Detection on 1 or all camera """
    al_cam = extract_arg(message.text)
    if len(al_cam) == 2: # check if concreting camera
        if al_cam[1].lower() == 'all':
            l_cam = base.cams_list()
        else:
            l_cam = base.selection(al_cam[1]) #selection 1 cam (first in list)
            if l_cam is None:
                bot.send_message(message.chat.id, 'Такая камера не найдена')
    else:
        l_cam = base.cams_list()
    if al_cam[0].lower() in ['on', 'off']: # check action for camera
        if al_cam[0].lower() == 'on':
            command = True
        else:
            command = False
        for cloud_id, address, name, _, _ in l_cam:
            cam = cams[name]
            if cam.login():
                cam.set_info('Detect.MotionDetect.[0].Enable', command) 
                cam.close()
            else:
                bot.send_message(message.chat.id, f'Не удалось  подключиться к камере {name}. IP: {address}.     CloudId: {cloud_id}')
    else:
        bot.send_message(message.chat.id, 'Неверная команда')
            



bot.infinity_polling()