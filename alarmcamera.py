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
        cam = DVRIPCam(addr[0], user='admin', password=secret.CAM_PASS)
        if cam.login():
            snap = cam.snapshot()
            for user in base.list_users(subs=True):
                bot.send_message(
                    user, f'Получена тревога с камеры {cam.get_info("ChannelTitle")[0]}\nВремя: {reply["StartTime"]}')
                bot.send_photo(user, snap)
            cam.close()

    except (KeyboardInterrupt, SystemExit):
        break

server.close()
sys.exit(1)
