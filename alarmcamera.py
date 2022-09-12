import json
import struct
import sys
from datetime import datetime
from os import path
from socket import AF_INET, SOCK_STREAM, SOCK_DGRAM, socket, gethostbyname, gethostname
from time import sleep

import telebot

import secret
from alarmdatabase import DataBaseBot
from dvrip import DVRIPCam # From NeiroN

s = socket(AF_INET, SOCK_DGRAM)
s.connect(("8.8.8.8", 80))

ALRM_ADDRESS = s.getsockname()[0]
ALRM_PORT = 15002

s.close()

server = socket(AF_INET, SOCK_STREAM)
server.bind((ALRM_ADDRESS, ALRM_PORT))
server.listen(5)

log = "log.txt"


def tolog(s):
    logfile = open(datetime.now().strftime("%Y_%m_%d_") + log, "a+")
    logfile.write(s)
    logfile.close()

DATABASE = 'data.db'
base = DataBaseBot(DATABASE)

bot = telebot.TeleBot(secret.TOKEN)

def check_cam_par():
    l_cams = base.cams_list()
    for cloud_id, address, name, user, password in l_cams:
        cam = DVRIPCam(address, user=user, password=password)
        if cam.login():
            try:
                alarm_par = cam.get_info("NetWork.AlarmServer.[0]")
                if not (alarm_par["Alarm"] and alarm_par["Enable"] and alarm_par["Server"]["Name"] == ALRM_ADDRESS):
                    alarm_par["Alarm"] = True
                    alarm_par["Enable"] = True
                    alarm_par["Server"]["Name"] = ALRM_ADDRESS
                    cam.set_info("NetWork.AlarmServer.[0]", alarm_par)
                    tolog(f"Change alarm parameters on {name} ({address}, {cloud_id})" + "\r\n")
                else:
                    tolog(f"Nothing change {name} ({address}, {cloud_id})" + "\r\n")
            except:
                tolog(f"Error on write parameter in {name} ({address}, {cloud_id})" + "\r\n")
            cam.close()
        else:
            tolog(f"Can't connect {name} ({address}, {cloud_id})" + "\r\n")

check_cam_par()

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
        tolog(repr(data) + "\r\n")
    except (KeyboardInterrupt, SystemExit):
        break

server.close()
sys.exit(1)
