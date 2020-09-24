import telebot as tb
import requests
import json
import base64
import os

with open('src/bot_conf.json', 'r') as conf_file:
    CONF = json.load(conf_file)

URL = 'http://' + CONF['discord_bot_host']
bot = tb.TeleBot(CONF['token'])


text_messages = {
    'help': '''
Private command:
/discord - get a invitation link of ACM discord server (once per user)

Group command:
/algun_comando - escribir la descripción del comando aquí
''',

    'welcome':
        u'@{name} Welcome to ACM group!',
    'link_invitation':
        u'@{name}, use this link {link} to join our discord server',
    'only_private_command':
        u'This command is only available in private, try to start a private conversation with me',
    'not_member':
        u'You must be a member of our telegram group',
    'discordlk_geted_already':
        u'You have already obtained the invitation link, contact the group administrator if you have problems'
}

text_server = {
    'error':
        u'Error: {detail}'
}

PERMITTED_ROLE_MEMBER = ('creator', 'administrator', 'member')
DISCORDLK_USERS_PATH = 'src/discordlk_geted_users.txt'

if not os.path.exists(DISCORDLK_USERS_PATH):
    with open(DISCORDLK_USERS_PATH, 'w'):
        pass

with open(DISCORDLK_USERS_PATH, 'r') as file:
    discordlk_geted_users = [line.strip() for line in file.readlines()]


def is_permitted_group(chat_id):
    """check if the command from message happened in a permitted telegram group

    Args:
        chat_id (int): id of the message object

    Returns:
        bool: True mean it is a permitted group and vice versa
    """
    return chat_id == int(CONF['permitted_group_id'])


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """send a list of commands to the new user or when they invoke help

    Args:
        message (telebot.Message):
    """
    bot.reply_to(message, text_messages['help'])


@bot.message_handler(func=lambda m: True, content_types=['new_chat_participant'])
def on_user_joins(message):
    """send a welcome message to new joined user (only permitted group)

    Args:
        message (telebot.Message): 
    """
    if not is_permitted_group(message.chat.id):
        return

    name = message.new_chat_participant.first_name
    if hasattr(message.new_chat_participant, 'last_name') and message.new_chat_participant.last_name is not None:
        name += u" {}".format(message.new_chat_participant.last_name)

    if hasattr(message.new_chat_participant, 'username') and message.new_chat_participant.username is not None:
        name += u" (@{})".format(message.new_chat_participant.username)

    bot.reply_to(message, text_messages['welcome'].format(name=name))


@bot.message_handler(commands=["discord"])
def get_discord_link(message):
    """send a invitation link of discord whe the user call this command as private and is a member of our permitted telegram group

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
        req = requests.post(URL + '/server/link_invitation', json={"user": {
            "username": CONF["host_username"], "password": CONF["host_password"]
        }})
        if req.text.startswith("https://"):
            bot.reply_to(message, text_messages['link_invitation'].format(
                name=message.from_user.first_name, link=req.text))

            if status == 'member':
                discordlk_geted_users.append(user_id)
                with open(DISCORDLK_USERS_PATH, 'a') as file:
                    file.write(user_id + '\n')
        else:
            print(req.text)
    except:
        print(text_server['error'].format(
            detail='no se ha podido comunicar con el servidor de discord bot o no hay permisos en el fichero'))


bot.polling(none_stop=False, interval=0, timeout=20)
