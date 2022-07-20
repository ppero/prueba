import os
import re
import time
import pytz
import zipfile
import requests
import traceback

from mega import Mega
from telethon import TelegramClient, events

from bs4 import BeautifulSoup
from datetime import datetime
from zipfile import ZipFile

# .env vars
from bot.config import (
    HOST, ACCOUNT, PASSWORD, OWNER,
    API_HASH, API_ID, TELEGRAM_TOKEN,
    MEGABYTES, PASS_MEGA, GMAIL_MEGA)

# Modulos
import bot.multiFile as multiFile
from bot.Client import MoodleClient

IST = pytz.timezone('Cuba')

links = []


# GESTION DE ARCHIVOS
def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


async def get_file_size(file):
    file_size = os.stat(file)
    return file_size.st_size


# SUBIR A MOODLE
async def upload_to_moodle(f, msg):
    # rand_user=Users_Data[random.randint(0,len(Users_Data)-1)]
    size = await get_file_size(f)
    try:
        start = time.time()
        await msg.edit(f'Subiendo...\n\nArchivo: {str(f)}\n\nTamaño: {sizeof_fmt(size)}')
        print(f'Subiendo... Archivo: {str(f)}\nTamaño: {sizeof_fmt(size)}')
        moodle = MoodleClient(f'{ACCOUNT}', f'{PASSWORD}')
        loged = moodle.login()
        if loged == True:
            evidence = moodle.createEvidence(f.split(".")[0])
            itemid = None
            moodle.upload_file(f, evidence, itemid)
            moodle.saveEvidence(evidence)

            await msg.edit(f'✅ Subido ✅')
            await msg.delete()
            end = time.time()
            t = end-start
            t1 = str(t).split(".")
            t1.pop(-1)
            tiempo = "".join(map(str, t1))

            print(f"Timepo de subida:{tiempo}")
            h = str(datetime.now().time()).split(".")
            h.pop(-1)
            #Hora="".join(map(str, h))
            await msg.respond(
                f'!Subido!\n\nArchivo: {str(f)}\n'
                'Tamaño: {str(sizeof_fmt(size))}\nTiempo: {str(tiempo)}s\n\n/files')
            print(
                f'Subido ✅\n\nArchivo: {str(f)}\nTamaño: {str(sizeof_fmt(size))}')

    except Exception as e:
        print(traceback.format_exc(), 'Error en el upload')
        await msg.edit(f'Error al Subir\n\nHay problemas con el Moodle')

# PROCESAR ARCHIVO ANTES DE SUBIR


async def process_file(file, bot, ev, msg):
    try:

        msgurls = ''
        maxsize = 1024 * 1024 * 1024 * 2
        file_size = await get_file_size(file)
        chunk_size = 1024 * 1024 * MEGABYTES

        if file_size > chunk_size:
            await msg.edit(
                f'Comprimiendo...\n\nArchivo: {str(file)}\n\nTamaño Total: {str(sizeof_fmt(file_size))}\n\n'
                f'Partes: {len(multiFile.files)} - {str(sizeof_fmt(chunk_size))}')
            print(
                f'Comprimiendo... Archivo: {str(file)}\nTamaño Total: {str(sizeof_fmt(file_size))}')
            mult_file = multiFile.MultiFile(file+'.7z', chunk_size)
            zip = ZipFile(mult_file,  mode='w',
                          compression=zipfile.ZIP_DEFLATED)
            zip.write(file)
            zip.close()
            mult_file.close()
            data = ''
            i = 0
            start = time.time()
            for f in multiFile.files:

                await msg.edit(
                    f'Subiendo...\n\nArchivo: {str(f)}\n\nTamaño: {str(sizeof_fmt(file_size))}\n\n'
                    f'Partes: {len(multiFile.files)} - {MEGABYTES} MB')
                print(
                    f'Subiendo... Archivo: {str(f)}\nTamaño: {str(sizeof_fmt(file_size))}')
                moodle = MoodleClient(f'{ACCOUNT}', f'{PASSWORD}')
                loged = moodle.login()
                if loged == True:
                    evidence = moodle.createEvidence(f.split(".")[0])
                    itemid = None
                    moodle.upload_file(f, evidence, itemid)
                    moodle.saveEvidence(evidence)

            await msg.edit(f'✅ Subido ✅')
            await msg.delete()
            end = time.time()
            t = end-start
            t1 = str(t).split(".")
            t1.pop(-1)
            tiempo = "".join(map(str, t1))

            print(f"Timepo de subida:{tiempo}")
            h = str(datetime.now(IST).time()).split(".")
            h.pop(-1)
            #Hora="".join(map(str, h))
            await msg.respond(
                f'Subido\n\nArchivo: {str(f)}\nTamaño Total: {str(sizeof_fmt(file_size))}\nPartes: {len(multiFile.files)}'
                f' - {str(sizeof_fmt(chunk_size))}\nTiempo: {str(tiempo)}s\n\n/files', parse_mode="Markdown")
            print(
                f'Subido ✅\n\nArchivo: {str(file)}\nTamaño: {str(sizeof_fmt(file_size))}')
        else:
            await upload_to_moodle(file, msg)
            os.unlink(file)

    except Exception as e:
        await msg.edit('(Error Subida) - ' + str(e))


async def processMy(ev, bot):
    try:
        text = ev.message.text
        message = await bot.send_message(ev.chat_id, '⚙️Procesando...')
        if ev.message.file:
            await message.edit(
                f'⚙️Descargando Archivo...\n\n🔖Archivo: {str(ev.message.file.name)}\n\n'
                f'📦Tamaño: {str(sizeof_fmt(ev.message.file.size))}')
            print(
                f'Descargando... Archivo: {str(ev.message.file.name)}\nTamaño: {str(sizeof_fmt(ev.message.file.size))}')
            file_name = await bot.download_media(ev.message)
            await process_file(file_name, bot, ev, message)
    except Exception as e:
        await bot.send_message(str(e))


async def down_mega(bot, ev, text):
    mega = Mega()
    msg = await bot.send_message(ev.chat_id, 'Procesando Enlace de MEGA...')
    try:
        mega.login(email=f'{GMAIL_MEGA}', password=f'{PASS_MEGA}')
    except:
        await msg.edit('❗️Error en la cuenta de MEGA❗️')
    try:
        await msg.edit(f'Descargando...\n\nArchivo:{str(text)}\nTamaño: {str(sizeof_fmt(mega.get_file_size(text)))}')
        path = mega.download_url(text)
        await msg.edit(f'Descargado\n\nAechivo: {path}')
        await process_file(str(path), bot, ev, msg)
    except:
        msg.edit('❗️Error en la Descarga❗️')
        print(traceback.format_exc())


def req_file_size(req):
    try:
        return int(req.headers['content-length'])
    except:
        return 0


def get_url_file_name(url, req):
    try:
        if "Content-Disposition" in req.headers.keys():
            return str(re.findall("filename=(.+)", req.headers["Content-Disposition"])[0])
        else:
            tokens = str(url).split('/')
            return tokens[len(tokens)-1]
    except:
        tokens = str(url).split('/')
        return tokens[len(tokens)-1]
    return ''


def save(filename, size):
    mult_file = multiFile.MultiFile(filename+'.7z', size)
    zip = ZipFile(mult_file,  mode='w', compression=zipfile.ZIP_DEFLATED)
    zip.write(filename)
    zip.close()
    mult_file.close()


async def upload_to_moodle_url(msg, bot, ev, url):
    await msg.edit('⚙️Analizando...')
    html = BeautifulSoup(url, "html.parser")
    print(html.find_all('apk'))
    req = requests.get(url, stream=True, allow_redirects=True)
    if req.status_code == 200:
        try:
            chunk_size = 1024 * 1024 * 49
            chunk_sizeFixed = 1024 * 1024 * 49
            filename = get_url_file_name(url, req)
            filename = filename.replace('"', "")
            file = open(filename, 'wb')
            await msg.edit(f'Descargando...\n\nArchivo: {str(filename)}\n\nTamaño: {str(sizeof_fmt(req_file_size(req)))}')

            print('Descargando...')
            for chunk in req.iter_content(chunk_size=chunk_sizeFixed):
                if chunk:
                    print(file.tell())
                    file.write(chunk)
                else:
                    print('no hay chunk')

            file.close()
            await process_file(file.name, bot, ev, msg)
        except:
            print(traceback.format_exc())

        multiFile.files.clear()
    pass


# PROCESO DE DESCARGA DE ARCHIVOS
async def dll(ev, bot, msg):
    global links
    for message in links:
        try:
            multiFile.clear()

            text = message.message.text
            if message.message.file:
                msg = await bot.send_message(
                    ev.chat_id,
                    f'Descargando...\n\nArchivo: {str(message.message.file.name)}\n\n'
                    f'Tamaño: {str(sizeof_fmt(message.message.file.size))}')
                print('Descargando...')
                file_name = await bot.download_media(message.message)
                await process_file(file_name, bot, ev, msg)
            elif 'mega.nz' in text:
                await down_mega(bot, ev, text)
            elif 'https' in text or 'http' in text:
                await upload_to_moodle_url(msg, bot, ev, url=text)
        except Exception as e:
            await bot.send_message(ev.chat_id, e)
    links = []


# PARTE DE LOS COMANDOS DEL BOT
bot = TelegramClient(
    'bot', api_id=API_ID,
    api_hash=API_HASH).start(
        bot_token=TELEGRAM_TOKEN)

action = 0
actual_file = ''


@bot.on(events.NewMessage())
async def process(ev: events.NewMessage.Event):
    global links
    text = ev.message.text
    file = ev.message.file
    user_id = ev.message.peer_id.user_id
    if user_id == OWNER:

        if '#watch' in text:
            await bot.send_message(ev.chat_id, '🕠Esperando...')
        elif 'mega.nz' in text:
            await bot.send_message(ev.chat_id, 'Enlace de MEGA Encontrado...\n/up')
            links.append(ev)

        elif 'https' in text or 'http' in text:
            await bot.send_message(ev.chat_id, 'Enlace Encontrado...\n/up')
            links.append(ev)
        elif file:
            await bot.send_message(ev.chat_id, 'Archivo Encontrado...\n/up')
            links.append(ev)
        elif ev.message.file:
            links.append(ev)
        elif '#clear' in text:
            links = []

# COMANDO START


@bot.on(events.NewMessage(pattern='/start'))
async def process(ev: events.NewMessage.Event):
    print('start...')
    user_id = ev.message.peer_id.user_id
    if user_id == OWNER:
        Hora = str(datetime.now(IST).time()).split(".")
        Hora.pop(-1)
        h = "".join(map(str, Hora))

        await bot.send_message(ev.chat_id, f'Se inicio correctamente el Bot\n\n❕Usa /info para saber más sobre mis funciones.')
    else:
        await bot.send_message(ev.chat_id, '❗️Acceso Denegado❗️')

# COMANDO INFO


@bot.on(events.NewMessage(pattern='/info'))
async def info(ev: events.NewMessage.Event):

    print('info...')
    user_id = ev.message.peer_id.user_id
    if user_id == OWNER:
        await bot.send_message(
            ev.chat_id,
            f'❕Información❕\n\n📡Moodle: {HOST}\n👤Usuario: <code>{ACCOUNT}</code>\n🔑Contraseña: <code>{PASSWORD}</code>\n'
            f'📚Tamaño de zip: {MEGABYTES}', parse_mode='HTML')
    else:

        await bot.send_message(ev.chat_id, '❗️Acceso Denegado❗️')

# COMANDO PRO


@bot.on(events.NewMessage(pattern='/pro'))
async def process(ev: events.NewMessage.Event):
    user_id = ev.message.peer_id.user_id
    if user_id == OWNER:
        await bot.send_message(ev.chat_id, f'📋Procesos:\n\n{len(links)}\n\n/up\n/clear')
    else:
        await bot.send_message(ev.chat_id, '❗️Acceso Denegado❗️')


# COMANDO CLEAR
@bot.on(events.NewMessage(pattern='/clear'))
async def process(ev: events.NewMessage.Event):
    user_id = ev.message.peer_id.user_id
    if user_id == OWNER:
        await bot.send_message(ev.chat_id, f'🗑 {len(links)} Procesos Limpiados 🗑\n/pro')
        links.clear()
    else:
        await bot.send_message(ev.chat_id, '❗️Acceso Denegado❗️')


@bot.on(events.NewMessage(pattern='/up'))
async def process(ev: events.NewMessage.Event):

    print('Up...')
    user_id = ev.message.peer_id.user_id
    if user_id == OWNER:
        msg = await bot.send_message(ev.chat_id, '🔬Procesando...')
        await dll(ev, bot, msg)
    else:
        await bot.send_message(ev.chat_id, '❗️Acceso Denegado❗️')


# COMANDO FILES
@bot.on(events.NewMessage(pattern='/files'))
async def process(ev: events.NewMessage.Event):
    print('files...')
    user_id = ev.message.peer_id.user_id
    if user_id == OWNER:

        message = await bot.send_message(ev.chat_id, 'Conectando...')

        moodle = MoodleClient(f'{ACCOUNT}', f'{PASSWORD}')
        loged = moodle.login()
        if loged:
            List = moodle.getEvidences()
            List1 = List[:45]
            total = len(List)
            List2 = List[46:]
            info1 = f'<b>Archivos: {str(total)}</b>\nEliminar todo: /del_all\n\n'
            info = f'<b>Archivos: {str(total)}</b>\nEliminar todo: /del_all\n\n'

            i = 1
            for item in List1:

                info += '<b>/del_'+str(i)+'</b> '
                #info += '<b>'+item['name']+':</b>\n'
                for file in item['files']:
                    info += '<a href="'+file['url'] + \
                        '">\t'+file['name']+'</a>\n'
                info += '\n'
                i += 1
                await message.edit(f'{info}', parse_mode="html")
            if len(List2) > 0:
                message1 = await bot.send_message(ev.chat_id, '🌐Conectando Lista 2...')
                for item in List2:

                    info1 += '<b>/del_'+str(i)+'</b> '
                    #info1 += '<b>'+item['name']+':</b>\n'
                    for file in item['files']:
                        info1 += '<a href="' + \
                            file['url']+'">\t'+file['name']+'</a>\n'
                    info1 += '\n'
                    i += 1
                    await message1.edit(f'{info1}', parse_mode="html")

    else:
        await bot.send_message(ev.chat_id, '❗️Acceso Denegado❗️')


# COMANDO DEL
@bot.on(events.NewMessage(pattern='/del'))
async def process(ev: events.NewMessage.Event):
    print('del...')

    message = await bot.send_message(ev.chat_id, 'Conectando...')
    index = int(ev.raw_text.split("_")[1]) - 1
    moodle = MoodleClient(f'{ACCOUNT}', f'{PASSWORD}')
    loged = moodle.login()
    if loged:
        list = moodle.getEvidences()
        if list != []:
            evid = list[index]
            await message.edit(f"<i>❗️Eliminando...\n\n📦Archivo: {evid['name']}</i>", parse_mode="html")
            print('Eliminando...')
            moodle.deleteEvidence(evid)
            await message.edit(f"<i>📦Archivo: {evid['name']}\n\n💢Archivo Eliminado💢</i>", parse_mode="html")
            print('Eliminado')
            moodle = MoodleClient(f'{ACCOUNT}', f'{PASSWORD}')
            loged = moodle.login()
            if loged:
                List = moodle.getEvidences()
                List1 = List[:45]
                total = len(List)
                List2 = List[46:]
                info1 = f'<b>Archivos Totales: {str(total)}</b>\nBorrado: /del_all'
                info = f'<b>Archivos Totales: {str(total)}</b>\nBorrado: /del_all'
                i = 1
                for item in List1:

                    info += '<b>/del_'+str(i)+'</b> 📦 '
                    #info += '<b>'+item['name']+':</b>\n'
                    for file in item['files']:
                        info += '<a href="'+file['url'] + \
                            '">\t'+file['name']+'</a>\n'
                    info += '\n'
                    i += 1
                    await message.edit(f'{info}', parse_mode="html")
                if len(List2) > 0:
                    message1 = await bot.send_message(ev.chat_id, 'Conectando...')
                    for item in List2:

                        info1 += '<b>/del_'+str(i)+'</b> 📦 '
                        #info1 += '<b>'+item['name']+':</b>\n'
                        for file in item['files']:
                            info1 += '<a href="' + \
                                file['url']+'">\t'+file['name']+'</a>\n'
                        info1 += '\n'
                        i += 1
                        await message1.edit(f'{info1}', parse_mode="html")
            else:
                await message.edit('❗️Acceso Denegado❗️')
        else:
            await message.edit("<i>❕No hay archivos que borrar❕</i>", parse_mode="html")
    else:
        await message.edit('❗️No se pudo conectar con la cuenta❗️')


@bot.on(events.NewMessage(pattern='/del_all'))
async def process(ev: events.NewMessage.Event):

    moodle = MoodleClient(f'{ACCOUNT}', f'{PASSWORD}')
    loged = moodle.login()
    if loged:

        list = moodle.getEvidences()
        lista = len(list)

        index = len(list)

        if index != 0:
            message = await bot.send_message(ev.chat_id, f'<i>Eliminando... todos los archivos en cuenta</i>', parse_mode="html")
            print('Eliminando...')
            for i in range(index):
                evid = list[i]
                moodle.deleteEvidence(evid)
                print('Eliminado')
            await message.edit(f'<i>Eliminación completada</i>', parse_mode="html")
            print('Eliminado')
        else:
            await bot.send_message(ev.chat_id, f'<i>❕No hay archivos que eliminar❕</i>', parse_mode="html")
    else:
        await bot.send_message(ev.chat_id, 'No se pudo conectar con la cuenta')

# COMANDO ZIP


@bot.on(events.NewMessage(pattern='/zip'))
async def info(ev: events.NewMessage.Event):
    zip = ev.message.text.split(' ')
    if len(zip) == 2:
        try:
            zip_mb = int(zip[1])
            if zip_mb > 0:
                MEGABYTES = zip_mb
                await bot.send_message(ev.chat_id, f'Tamaño de zip establecido a {MEGABYTES} MB ')
            else:
                await bot.send_message(ev.chat_id, f'El tamaño de zip debe ser mayor a 0')
        except:
            await bot.send_message(ev.chat_id, f'El tamaño de zip debe ser un número')

# COMANDO ACC


@bot.on(events.NewMessage(pattern='/acc'))
async def info(ev: events.NewMessage.Event):
    user = ev.message.text.split(' ')[1]
    passw = ev.message.text.split(' ')[2]
    ACCOUNT = user
    PASSWORD = passw
    await bot.send_message(ev.chat_id, f'Cuenta establecida a {ACCOUNT} {PASSWORD}')

# COMANDO HOST


@bot.on(events.NewMessage(pattern='/host'))
async def info(ev: events.NewMessage.Event):
    host = ev.message.text.split(' ')[1]
    HOST = host
    await bot.send_message(ev.chat_id, f'Host establecido a {HOST}')


@bot.on(events.NewMessage(pattern='/sel'))
async def process(ev: events.NewMessage.Event):

    Li = int(ev.message.text.split(' ')[1])-1
    Ls = int(ev.message.text.split(' ')[2])
    print(Li)
    print(Ls)
    message = await bot.send_message(ev.chat_id, 'Conectando...')

    moodle = MoodleClient(f'{ACCOUNT}', f'{PASSWORD}')
    loged = moodle.login()

    list = moodle.getEvidences()
    index = len(list)

    d = Ls-Li
    info = f'<b>Archivos Eliminados: {str(d)}</b>\n\n'
    for i in range(d):

        Ls -= 1
        if list != []:
            if Li <= Ls:
                evid = list[Ls]
                await message.edit(f"<i>Eliminando...\n\nArchivo: {evid['name']}</i>", parse_mode="html")
                print('Eliminando...')
                moodle.deleteEvidence(evid)
                await message.edit(f"<i>Archivo: {evid['name']}\n\nArchivo Eliminado</i>", parse_mode="html")
                print('Eliminado')
                info += '<b> Archivo:'+evid['name']+'Eliminado</b>\n'
                await message.edit(f'{info}', parse_mode="html")
                moodle = MoodleClient(f'{ACCOUNT}', f'{PASSWORD}')
                loged = moodle.login()

print('Running without errors')
bot.loop.run_forever()
