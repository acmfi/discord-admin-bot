# Configuración

Crear y modificar el fichero src/bot_conf.json con el siguiente formato

```json
{
    "token": "token del bot de telegram",
    "permitted_group_id":"restringir que un único grupo de telegram pueda usar este bot",
    "discord_bot_host": "host del bot de discord donde desea enviar los mensajes del canal con su puerto, si estas en el mismo equipo prueba localhost:5000",
    "host_username": "usuario para acceder al host",
    "host_password": "contraseña del usuario"
}
```