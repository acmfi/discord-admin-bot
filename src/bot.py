import telebot as tb
import requests
import json
import base64

CONF = json.load(open('src/bot_conf.json', 'r'))

URL = 'http://' + CONF['discord_bot_host']
bot = tb.TeleBot(CONF['token'])


text_messages = {
    'welcome':
        u'Welcome to ACM group{name}!',
    'link_invitation':
        u'@{name}, use this link {link} to join our discord server',
    'only_private_command':
        u'This command is only available in private, try to start a private conversation with me',
    'not_member':
        u'You must be a member of our telegram group'
}

text_server = {
    'error':
        u'Error en la conexión'
}


def is_permitted_group(chat_id):
    return chat_id == int(CONF['permitted_group_id'])


@bot.channel_post_handler(content_types=['text', 'photo'])
def resend_text_to_discord(post):
    """create a request of http (post) to the discord bot server when the bot received a post of the channel

    Args:
        post (telebot.Post): the new post of the channel received recently
    """
    image_str = None
    if post.photo:
        downloaded_file = bot.download_file(
            bot.get_file(post.photo[-1].file_id).file_path)
        image_byte = base64.b64encode(downloaded_file)
        image_str = image_byte.decode('ascii')
    aviso = {"text": post.text, "caption": post.caption, "photo": image_str,
             "user": {
                 "username": CONF["host_username"], "password": CONF["host_password"]
             }}
    try:
        req = requests.post(URL + '/sendChannelPost', json=aviso)
        if req.text != "OK":
            print(req.text)
    except:
        print(text_server['error'])


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

    if not bot.get_chat_member(int(CONF['permitted_group_id']), message.from_user.id):
        bot.reply_to(message, text_messages['not_member'])
        return

    try:
        req = requests.post(URL + '/server/link_invitation', json={"user": {
            "username": CONF["host_username"], "password": CONF["host_password"]
        }})
        if req.text.startswith("https://"):
            bot.reply_to(message, text_messages['link_invitation'].format(
                name=message.from_user.first_name, link=req.text))
        else:
            print(req.text)
    except:
        print(text_server['error'])


bot.polling(none_stop=False, interval=0, timeout=20)
