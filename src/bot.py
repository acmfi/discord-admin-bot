import datetime
import telebot as tb
import requests
import json
import base64
import os

with open('src/bot_conf.json', 'r') as conf_file:
    CONF = json.load(conf_file)

HOST_URL = 'http://' + CONF['discord_bot_host']
bot = tb.TeleBot(CONF['token'])

text_messages = {
    'help': '''
Comandos privados:
/discord - conseguir el link de invitación del servidor discord de ACM (un link por usuario)

Comandos de grupo:
/algun_comando - todavía en construcción...
''',

    'welcome':
        u'@{name} Bienvenido al grupo de ACM!',
    'link_invitation':
        u'@{name}, usa este link {link} para unir a nuestro servidor de discord',
    'only_private_command':
        'Este comando es privado, intenta iniciar una conversación privada con el bot',
    'not_member':
        'Tienes que ser un miembro de nuestro grupo de Telegram',
    'discordlk_geted_already':
        'Ya habias obtenido un link, contacte con nuestro administrador de grupo si tienes problemas',
    'connection_failed':
        'En estos momentos no se encuentra disponible el bot de discord'
}

text_server = {
    'error':
        u'Error: {detail}'
}

PERMITTED_ROLE_MEMBER = ('creator', 'administrator', 'member')
DISCORDLK_USERS_PATH = 'src/discordlk_geted_users.txt'
token_info = None

if not os.path.exists(DISCORDLK_USERS_PATH):
    with open(DISCORDLK_USERS_PATH, 'w'):
        pass

with open(DISCORDLK_USERS_PATH, 'r') as file:
    discordlk_geted_users = [line.strip() for line in file.readlines()]


def discord_bot_api_login():
    """try to login discord bot when token does not exist or token was expired

    Returns:
        Response: response object as result of requests to login or None if was logged
    """
    global token_info

    if token_info and datetime.datetime.fromtimestamp(token_info['exp'], tz=datetime.timezone.utc) >= (datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(minutes=1)):
        return

    response = requests.get(
        HOST_URL+'/login', auth=(CONF["host_username"], CONF["host_password"]))

    response.raise_for_status()
    if response:
        token_info = response.json()

    return response


def is_permitted_group(chat_id):
    """check if the command from message happened in a permitted telegram group

    Args:
        chat_id (int): id of the message object

    Returns:
        bool: True mean it is a permitted group and vice versa
    """
    return chat_id == int(CONF['permitted_group_id'])


@ bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """send a list of commands to the new user or when they invoke help

    Args:
        message (telebot.type.Message):
    """
    bot.reply_to(message, text_messages['help'])


@ bot.message_handler(func=lambda m: True, content_types=['new_chat_participant'])
def on_user_joins(message):
    """send a welcome message to new joined user (only permitted group)

    Args:
        message (telebot.type.Message):
    """
    if not is_permitted_group(message.chat.id):
        return

    name = message.new_chat_participant.first_name
    if hasattr(message.new_chat_participant, 'last_name') and message.new_chat_participant.last_name is not None:
        name += u" {}".format(message.new_chat_participant.last_name)

    if hasattr(message.new_chat_participant, 'username') and message.new_chat_participant.username is not None:
        name += u" (@{})".format(message.new_chat_participant.username)

    bot.reply_to(message, text_messages['welcome'].format(name=name))


@ bot.channel_post_handler(content_types=['text', 'photo'])
def resend_text_to_discord(post):
    """create a request of http (post) to the discord bot server when the bot received a post of the channel

    Args:
        post (telebot.Post): the new post of the channel received recently
    """
    try:
        discord_response = discord_bot_api_login()
    except Exception as err:
        print(text_server['error'].format(
            detail=f'connection failed: {err}'))
        return

    if discord_response is not None and not discord_response:
        print(text_server['error'].format(
            detail=f'could not login {discord_response.content}'))

    image_str = None
    if post.photo:
        downloaded_file = bot.download_file(
            bot.get_file(post.photo[-1].file_id).file_path)
        image_byte = base64.b64encode(downloaded_file)
        image_str = image_byte.decode('ascii')
    aviso = {"text": post.text, "caption": post.caption, "photo": image_str}
    try:
        response = requests.post(
            HOST_URL + '/server/channel/text/send_notice', json=aviso, params={'token': token_info['token']})
        if not response:
            print(text_server['error'].format(
                detail=f'discord bot connection failed {response.content}'))
    except Exception as err:
        print(text_server['error'].format(
            detail=f'discord bot connection failed {err}'))


@ bot.message_handler(commands=["discord"])
def get_discord_link(message):
    """send a invitation link of discord when the user call this command as private and is a member of our permitted telegram group

    Args:
        message (telebot.Message):
    """

    if message.chat.type != 'private':
        bot.reply_to(message, text_messages['only_private_command'])
        return

    status = bot.get_chat_member(
        int(CONF['permitted_group_id']), message.from_user.id).status
    if not status in PERMITTED_ROLE_MEMBER:
        bot.reply_to(message, text_messages['not_member'])
        return

    user_id = str(message.from_user.id)
    if status == 'member' and user_id in discordlk_geted_users:
        bot.reply_to(message, text_messages['discordlk_geted_already'])
        return

    try:
        discord_response = discord_bot_api_login()
    except Exception as err:
        bot.reply_to(message, text_messages['connection_failed'])
        return
    if discord_response is not None and not discord_response:
        bot.reply_to(message, text_messages['connection_failed'])

    try:
        response = requests.get(
            HOST_URL + '/server/link_invitation', params={'token': token_info['token']})
        if response:
            bot.reply_to(message, text_messages['link_invitation'].format(
                name=message.from_user.first_name, link=response.json()['link']))

            if status == 'member':
                discordlk_geted_users.append(user_id)
                with open(DISCORDLK_USERS_PATH, 'a') as file:
                    file.write(user_id + '\n')
        else:
            print(text_server['error'].format(
                detail=f'discord bot connection failed {response.content}'))
    except Exception as err:
        print(text_server['error'].format(
            detail=f'other error occurred {err}'))


bot.polling(none_stop=False, interval=0, timeout=20)
