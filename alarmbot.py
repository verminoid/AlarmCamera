
from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from dvrip import DVRIPCam #from NeiroNx
import secret
from alarmdatabase import DataBaseBot
import alarmcamera

DATABASE = 'data.db'

base = DataBaseBot(DATABASE)
bot = TeleBot(secret.TOKEN)


def extract_arg(arg):
    """извлечение аргументов"""
    return arg.split()[1:]


def extract_1_arg(arg):
    """извлечение длинного аргумента"""
    return arg.split(maxsplit=1)[1:]


keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
kb_snap = KeyboardButton('/snapshot')
kb_alarm_on = KeyboardButton('/alarm on')
kb_alarm_off = KeyboardButton('/alarm off')

keyboard.row(kb_snap)
keyboard.row(kb_alarm_on, kb_alarm_off)

@bot.message_handler(commands=['start'])
def start_handler(message):
    """ start проверяет пароль"""
    qstart = extract_arg(message.text)
    if base.user_exists(message.from_user.id):
        bot.send_message(message.chat.id,
                        f"{message.from_user.first_name}, Я уже вас видел, для помощи - /help", reply_markup=keyboard)
    else:
        if len(qstart):
            if qstart[0] == str(secret.BOT_PASS):
                base.new_user(
                    message.from_user.id, message.from_user.username, message.from_user.first_name, subs=True)
                bot.send_message(
                    message.chat.id,
                    f"Я вас запомнил, {message.from_user.first_name}!\nВы автоматически подписаны на тревожные оповещения\nЧтобы узнать, что я могу, введите /help ", reply_markup=keyboard)
                
            else:
                bot.reply_to(message, "кодовая фраза не верна")
        else:
            bot.send_message(message.chat.id, f"{message.from_user.first_name}, Вы не туда попали!")

@bot.message_handler(commands=['help'], func=lambda message: base.user_exists(message.from_user.id))
def help_hedler(message):
    bot.send_message(message.chat.id, 
            "Введи команду /snapshot чтобы получить картинки со всех камер. Если добавить название камеры получишь картинку с конкретной камеры.")
    bot.send_message(message.chat.id,
            "Введи команду /alarm on или off чтобы включить или выключить детектор движения на всех камерах. Если добавить название камеры то управляется только она.")
    bot.send_message(message.chat.id,
            "Введи команду /subs on или off чтобы включить или выключить подписку на оповещения по детектору движения на камерах.")
    bot.send_message(message.chat.id,
            "Введи команду /new_cam IP USER PASSWORD чтобы добавить камеру в базу данных.")
    bot.send_message(
        message.chat.id, "Приятного пользования!", reply_markup=keyboard)

@bot.message_handler(commands=['snapshot'], func=lambda message: base.user_exists(message.from_user.id))
def get_snapshot(message):
    """get snapshot from all camera

    """    
    cam_name = extract_1_arg(message.text)
    if len(cam_name) == 0:
        l_cams = base.cams_list()
    else:
        l_cams = base.cam_selection(cam_name[0])
    for cloud_id, address, name, user, password in l_cams:
        cam = DVRIPCam(address, user=user, password=password)
        if cam.login():
            try:
                snap = cam.snapshot()
                bot.send_photo(message.from_user.id, snap, caption=name, reply_markup=keyboard)
            except:
                bot.send_message(message.chat.id, f'Не удалось получить картинку с камеры {name}. IP: {address}. CloudId: {cloud_id}', reply_markup=keyboard)
            cam.close()
        else:
            bot.send_message(message.chat.id, f'Не удалось  подключиться к камере {name}. IP: {address}.     CloudId: {cloud_id}', reply_markup=keyboard)
        

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
            alarmcamera.check_cam_par()
            bot.send_message(message.chat.id, f'Камера {name}({cloud_id},{n_cam[0]}) успешно добавлена.', reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, 'Не удалось подключиться к камере с данными параметрами', reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, 'Введите имя пользователя и пароль')

@bot.message_handler(commands=['alarm'], func=lambda message: base.user_exists(message.from_user.id))
def alarm_on_off(message):
    """On/off Motion Detection on 1 or all camera """
    al_cam = extract_arg(message.text)
    if len(al_cam) == 2: # check if concreting camera
        if al_cam[1].lower() == 'all':
            l_cam = base.cams_list()
        else:
            l_cam = base.cam_selection(al_cam[1]) #selection 1 cam (first in list)
            if l_cam is None:
                bot.send_message(message.chat.id, 'Такая камера не найдена', reply_markup=keyboard)
    else:
        l_cam = base.cams_list()
    if al_cam[0].lower() in ['on', 'off']: # check action for camera
        if al_cam[0].lower() == 'on':
            command = True
        else:
            command = False
        for cloud_id, address, name, user, password in l_cam:
            cam = DVRIPCam(address, user=user, password=password)
            if cam.login():
                cam.set_info('Detect.MotionDetect.[0].Enable', command)
                bot.send_message(message.chat.id, f'Камера {name} Alarm: {al_cam[0].lower()}', reply_markup=keyboard)
                cam.close()
            else:
                bot.send_message(message.chat.id, f'Не удалось  подключиться к камере {name}. IP: {address}.     CloudId: {cloud_id}', reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, 'Неверная команда', reply_markup=keyboard)
            
@bot.message_handler(commands=['subs'], func=lambda message: base.user_exists(message.from_user.id))
def subscribe_on_off(message):
    query = extract_1_arg(message.text)
    if len(query) and query[0].lower() in ['on', 'off']:
        if query[0].lower() == 'on':
            base.subs_user(message.from_user.id, True)
            bot.send_message(message.chat.id, 'Вы подписаны на оповещения', reply_markup=keyboard)
        else:
            base.subs_user(message.from_user.id, False)
            bot.send_message(message.chat.id, 'Подписка на оповещения удалена', reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, 'Неправильная команда, добавьте "on" или "off" ', reply_markup=keyboard)

@bot.message_handler(commands=['edit_cam'], func=lambda message: base.user_exists(message.from_user.id))
def edit_cam_address(message):
    query = extract_arg(message.text)
    if len(query) == 2:
        cloud_id = query[0]
        address = query[1]
        base.cam_edit(cloud_id, address)
        alarmcamera.check_cam_par()
        bot.send_message(message.chat.id, f'Локальный адрес камеры {cloud_id} изменен на: {address}', reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, 'Неправильный запрос. введите /edit_cam cloud_id ip', reply_markup=keyboard)

def main():
    bot.infinity_polling()


if __name__ == '__main__':
    main()
