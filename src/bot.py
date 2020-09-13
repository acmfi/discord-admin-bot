import telebot as tb
import requests
import json
import base64

CONF = json.load(open('src/bot_conf.json', 'r'))

URL = 'http://' + CONF['discord_bot_host'] + '/sendChannelPost'
tele_bot = tb.TeleBot(CONF['token'])


@tele_bot.channel_post_handler(content_types=['text', 'photo'])
def resend_text_to_discord(post):
    """create a request of http (post) to the discord bot server when the bot received a post of the channel

    Args:
        post (telebot.post): the new post of the channel received recently
    """
    image_str = None
    if post.photo:
        downloaded_file = tele_bot.download_file(
            tele_bot.get_file(post.photo[-1].file_id).file_path)
        image_byte = base64.b64encode(downloaded_file)
        image_str = image_byte.decode('ascii')
    aviso = {"text": post.text, "caption": post.caption, "photo": image_str,
             "user": {
                 "username": CONF["host_username"], "password": CONF["host_password"]
             }}
    try:
        req = requests.post(URL, json=aviso)
        if req.text != "OK":
            print(req.text)
    except:
        print('Error en la conexion, post no enviado')


tele_bot.polling(none_stop=False, interval=0, timeout=20)
