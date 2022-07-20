from os import getenv

# TELEGRAM
OWNER = int(getenv('OWNER'))
if OWNER is None:
    raise Exception("id de telegram") 

API_ID = int(getenv('API_ID'))
if API_ID is None:
    raise Exception("api id de telegram") 

API_HASH = getenv('API_HASH')
if API_HASH is None:
    raise Exception("api hash de telegram") 

TELEGRAM_TOKEN = getenv('TELEGRAM_TOKEN')
if TELEGRAM_TOKEN is None:
    raise Exception("token del bot de telegram") 

# DATOS DEL MOODLE
HOST = getenv('HOST')
if HOST is None:
    raise Exception("url de la nube") 

ACCOUNT = getenv('ACCOUNT')
if ACCOUNT is None:
    raise Exception("user de la moodle") 

PASSWORD = getenv('PASSWORD')
if PASSWORD is None:
    raise Exception("contraseña de la moodle") 

# CUENTA DE MEGA
PASS_MEGA = getenv('PASS_MEGA')
if PASS_MEGA is None:
    raise Exception("contraseña de mega") 

GMAIL_MEGA = getenv('GMAIL_MEGA')
if GMAIL_MEGA is None:
    raise Exception("gmail de mega") 

# ARCHIVOS
MEGABYTES = int(getenv('MEGABYTES'))
if MEGABYTES is None:
    raise Exception("150") 
