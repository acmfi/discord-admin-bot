# Configuración

Crear y modificar el fichero src/bot_conf.json con el siguiente formato. Todo los servicios de este bot este limitado solo para un único grupo de telegram para evitar posibles fugas de información y aquellos usuarios que forman parte de este grupo, esto es posible con la configuración de la clave "permitted_group_id", para conseguir el ID del grupo consulte la siguiente [página](https://plexadictos.wordpress.com/2018/03/15/crear-un-bot-y-un-grupo-en-telegram-para-obtener-el-token-y-el-group-id/)

```json
{
    "token": "token del bot de telegram",
    "permitted_group_id":"restringir que un único grupo de telegram pueda usar este bot",
    "discord_bot_host": "host del bot de discord donde desea enviar los mensajes del canal con su puerto, si estas en el mismo equipo prueba localhost:5000",
    "host_username": "usuario para acceder al host",
    "host_password": "contraseña del usuario"
}
```