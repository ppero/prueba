## Deploy a Heroku
[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/ravenclawldz/moodle-uploader)

### Deploy a VPS

```sh
git clone https://github.com/ravenclawldz/moodle-uploader
cd moodle-uploader
pip3 install -r requirements.txt
# <Configura las variables de entorno>
python3 main.py
```

## Variables de Entorno
### TELEGRAM
- `API_ID`: Crea una aplicación en [my.telegram.org](https://my.telegram.org).
- `API_HASH`: Crea una aplicación en [my.telegram.org](https://my.telegram.org).
- `TELEGRAM_TOKEN`: Crea un bot de telegram en [@BotFather](https://t.me/BotFather).
- `OWNER`: Tu User Telegram ID. Enviale un mensaje a [@ShowJsonBot](https://t.me/ShowJsonBot) y copia el texto "id" para obtenerlo.
### MEGA
- `GMAIL_MEGA`: Credenciales de tu cuenta de MEGA.
- `PASS_MEGA`: Credenciales de tu cuenta de MEGA.
### MOODLE/NUBE
- `HOST`: URL del Moodle o NextCloud. Ejemplo: https://aulavirtual.hlg.sld.cu/
- `ACCCOUNT`: Credenciales de tu cuenta de Moodle o NextCloud.
- `PASSWORD`: Credenciales de tu cuenta de Moodle o NextCloud.
