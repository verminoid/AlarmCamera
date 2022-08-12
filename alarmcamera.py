import json
import struct
import sys
from datetime import datetime
from os import path
from socket import AF_INET, SOCK_STREAM, socket
from time import sleep

import telebot

import secret
from alarmdatabase import DataBaseBot
from dvrip import DVRIPCam # From NeiroN

ALRM_ADDRESS = "0.0.0.0"
ALRM_PORT = 15002

server = socket(AF_INET, SOCK_STREAM)
server.bind((ALRM_ADDRESS, ALRM_PORT))
server.listen(5)

DATABASE = 'data.db'
base = DataBaseBot(DATABASE)

bot = telebot.TeleBot(secret.TOKEN)

while True:
    try:
        conn, addr = server.accept()
        head, version, session, sequence_number, msgid, len_data = struct.unpack(
            "BB2xII2xHI", conn.recv(20)
        )
        sleep(0.1)  # Just for recive whole packet
        data = conn.recv(len_data)
        conn.close()
        reply = json.loads(data)
        print(datetime.now().strftime("[%Y-%m-%d %H:%M:%S]>>>"))
        print(head, version, session, sequence_number, msgid, len_data)
        print(json.dumps(reply, indent=4))
        print("<<<")
        cam = DVRIPCam(addr[0], user='admin', password=secret.CAM_PASS)
        cam.login()
        snap = cam.snapshot()
        for user in base.list_users():
            bot.send_message(
                user, f'Получено сообщение с камеры по адресу {addr[0]}:\n{json.dumps(reply, indent=4)}')
            bot.send_photo(user, snap)
        cam.close()

    except (KeyboardInterrupt, SystemExit):
        break

server.close()
sys.exit(1)
