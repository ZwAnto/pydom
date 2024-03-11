import base64
import json
import os
import platform
import ssl
import subprocess

import requests
import websockets
from fastapi import Depends, HTTPException
from requests.auth import HTTPDigestAuth

from pydom import config

tydom = None


# Generate 16 bytes random key for Sec-WebSocket-Keyand convert it to base64
def generate_random_key():
    return base64.b64encode(os.urandom(16))


def pingOk(sHost):
    try:
        _ = subprocess.check_output(
            "ping -{} 1 {}".format(
                "n" if platform.system().lower() == "windows" else "c", sHost
            ),
            shell=True,
        )
    except Exception:
        return False
    return True


# Initiate socket connection
async def socket_connect(headers={}):
    headers = {**headers, "Authorization": build_digest_headers()}
    return await websockets.connect(
        f"wss://{config.TYDOM_HOST}:443/mediation/client?mac={config.TYDOM_MAC}&appli=1",
        extra_headers=headers,
        ssl=ssl._create_unverified_context(),
        open_timeout=None,
        close_timeout=None,
    )


def first_handshake():
    httpHeaders = {
        "Connection": "Upgrade",
        "Upgrade": "websocket",
        "Host": config.TYDOM_HOST + ":443",
        "Accept": "*/*",
        "Sec-WebSocket-Key": generate_random_key(),
        "Sec-WebSocket-Version": "13",
    }

    return requests.get(
        f"https://{config.TYDOM_HOST}:443/mediation/client?mac={config.TYDOM_MAC[-6:]}&appli=1",
        headers=httpHeaders,
        verify=False,
    )


def check_pairing():
    res = first_handshake()
    return "WWW-Authenticate" not in res.headers.keys()


def build_digest_headers():
    res = first_handshake()

    nonce = res.headers.get("WWW-Authenticate").split(",", 3)
    nonce = nonce[2].split("=", 1)[1].split('"')[1]

    digestAuth = HTTPDigestAuth(config.TYDOM_MAC[-6:], config.TYDOM_PASSWORD)
    chal = dict()
    chal["nonce"] = nonce
    chal["realm"] = "ServiceMedia"
    chal["qop"] = "auth"
    digestAuth._thread_local.chal = chal
    digestAuth._thread_local.last_nonce = nonce
    digestAuth._thread_local.nonce_count = 1
    return digestAuth.build_digest_header(
        method="GET",
        url=f"https://{config.TYDOM_HOST}:443/mediation/client?mac={config.TYDOM_MAC[-6:]}&appli=1",
    )


async def socket_check_v2():
    global tydom

    if not pingOk(config.TYDOM_HOST):
        raise HTTPException(status_code=503, detail="Tydom can't be reached")

    if tydom is None or not tydom.open:
        websocketHeaders = {"Authorization": build_digest_headers()}

        try:
            tydom = await socket_connect(websocketHeaders)
        except Exception:
            raise HTTPException(status_code=503, detail="Tydom can't be reached")

    if tydom is None or not tydom.open:
        raise HTTPException(status_code=503, detail="Tydom can't be reached")

    return tydom


async def socket_shutdown():
    global tydom

    if tydom is not None and tydom.open:
        await tydom.close()
        await tydom.wait_closed()

    return


class Tydom:
    def __init__(self, socket=Depends(socket_check_v2)):
        self.socket = socket


async def send_message(websocket, method, path, data=""):
    data = json.dumps(data).encode("utf-8")

    str = f"{method} {path} HTTP/1.1\r\nContent-Length: {len(data)}\r\nContent-Type: application/json; charset=UTF-8\r\nTransac-Id: 0\r\n\r\n"
    a_bytes = bytes(str, "ascii")
    a_bytes += data

    await websocket.send(a_bytes)
    return await websocket.recv()


def parse_response(r):
    header, content = r.decode("utf-8").split("\r\n\r\n")[:2]
    header = {i.split(":")[0]: i.split(": ")[1] for i in header.split("\r\n")[1:]}

    if header.get("Content-Length", "") != "0":
        if header.get("Content-Type", "") == "application/json":
            if header.get("Transfer-Encoding", "") == "chunked":
                content = json.loads("".join(content.split("\r\n")[1::2]))
            else:
                content = json.loads("".join(content.split("\r\n")))

    return {"header": header, "content": content}
