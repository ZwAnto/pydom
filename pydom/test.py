import websockets
import asyncio
from pydom.socket import build_digest_headers
from ssl import _create_unverified_context
import json


class Tydom:
    def __init__(self, ip, mac, password):
        self.ip = ip
        self.mac = mac
        self.password = password

        self.websocket = None

    def __connect(self):
        self.websocketHeaders = {
            "Authorization": build_digest_headers(self.ip, self.mac, self.password)
        }

        return websockets.connect(
            "wss://{}:443/mediation/client?mac={}&appli=1".format(self.ip, self.mac),
            extra_headers=self.websocketHeaders,
            ssl=_create_unverified_context(),
            open_timeout=None,
        )

    def run(self, request):
        asyncio.run(self.test(request))

    async def test(self, request):
        if self.websocket is None or not self.websocket.open:
            self.websocket = await self.__connect()

        data = json.dumps(request.get("content", "")).encode("utf-8")

        str = f"{request['method']} {request['endpoint']} HTTP/1.1\r\nContent-Length: {len(data)}\r\nContent-Type: application/json; charset=UTF-8\r\nTransac-Id: 0\r\n\r\n"
        a_bytes = bytes(str, "ascii")
        a_bytes += data
        await self.websocket.send(a_bytes)
        test = await self.websocket.recv()

        print(test)


tydom = Tydom(HOST, MAC, PASSWORD)

tydom.run(
    {
        "method": "GET",
        "endpoint": "/info",
    }
)
