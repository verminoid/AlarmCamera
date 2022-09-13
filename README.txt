# AlarmCamera

Creation of a server for receiving messages from cameras as well as managing functions through a telegram bot
using pyTelegramBotAPI from pip and camera control library from https://github.com/NeiroNx/python-dvr

for working we need create config file "secret.py" with: 

'
TOKEN = 'token-code from telegram'
CAM_PASS = 'password for cam'
BOT_PASS = 'password for starting using bot by user'
'

database create automatic in sqlite 'data.db'
