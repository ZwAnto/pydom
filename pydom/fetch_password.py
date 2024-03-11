import asyncio

import re
import subprocess

from pydom.socket import (
    check_pairing,
    socket_connect,
    send_message,
    parse_response,
    Tydom,
)
from pydom import config


config.TYDOM_HOST

from time import sleep


async def update_password():
    print("Waiting for pairing mode...")
    while not check_pairing():
        sleep(5)

    print("Retrieving passsword...")
    socket = await socket_connect()
    response = await send_message(socket, "GET", "/configs/gateway/password")
    response = parse_response(response)

    password = response["content"]["current"]

    print(password)
    return password
    # https://superuser.com/a/976712
    # exit_code = subprocess.check_call(['sed', '-i', f'/^TYDOM_PASSWORD=/{{h;s/=.*/={re.escape(password)}/}};${{x;/^$/{{s//TYDOM_PASSWORD={re.escape(password)}/;H}};x}}', '.env'])
    return exit_code


asyncio.run(update_password())


async def test():
    socket = await socket_connect()
    r = await send_message(socket, "GET", "/info")
    return parse_response(r)


asyncio.run(test())
