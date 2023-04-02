from datetime import datetime
from pathlib import Path

import urllib3
from fastapi import Depends, FastAPI, Request
from fastapi.responses import FileResponse, PlainTextResponse

import pydom
from pydom.models import *
from pydom.socket import (Tydom, parse_response, send_message, socket_check_v2,
                          socket_shutdown)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    pass

@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse(str(Path(pydom.__path__[0]) / 'assets/favicon-196x196.png'))


@app.get('/metrics', response_class=PlainTextResponse)
async def metrics(tydom: Tydom=Depends(Tydom)):

    
    body = []

    r = await send_message(tydom.socket, "POST", "/refresh/all")
    r = await send_message(tydom.socket, "GET", "/devices/data")
    data = parse_response(r)

    try:
        for device in data['content']:
            for endpoint in device['endpoints']:
                for entry in endpoint['data']:
                    if entry['name'] in ['temperature', 'energyTotIndexGas', 'energyIndexHeatGas', 'energyIndexECSGas', 'outTemperature', 'setpoint']:
                        body.append(f'{entry["name"]} {{device="{device["id"]}", entrypoint="{endpoint["id"]}"}} {entry["value"]} {int(datetime.now().timestamp())*1000}')
    except:
        pass

    return '\n'.join(body) + '\n'


# protocols or info
@app.get("/{par}")
async def root(par: RootType, request: Request, tydom: Tydom=Depends(Tydom)):
    r = await send_message(tydom.socket, 'GET', request.scope['path'])
    return parse_response(r)

# /configs/file	Get tydom user config
# /groups/file	Get tydom groups config
# /moments/file	Get tydom moments config
# /scenarios/file	Get tydom scenarios config
@app.get("/{par}/file")
async def file(par: FileType, tydom: Tydom=Depends(Tydom)):
    r = await send_message(tydom.socket, "GET", f"/{par}/file")
    return parse_response(r)

# /devices/data	Get tydom devices data/state
# /devices/meta	Get tydom devices meta
# /devices/cmeta	Get tydom devices command meta
@app.get("/devices/{par}")
async def device(par: DeviceType, tydom: Tydom=Depends(Tydom)):
    r = await send_message(tydom.socket, 'GET', f"/devices/{par}")
    return parse_response(r)

# POST	/refresh/all	Force refresh tydom devices data
@app.post("/refresh/all")
async def refresh(tydom: Tydom=Depends(Tydom)):
    r = await send_message(tydom.socket, "POST", "/refresh/all")
    return parse_response(r)

# GET	/devices/${DEVICE_ID}/endpoints/${DEVICE_ID}/data	GET tydom device data/state
@app.get("/devices/{id}/data")
async def device_data(id, tydom: Tydom=Depends(Tydom)):
    r = await send_message(tydom.socket, "GET", f"/devices/{id}/endpoints/{id}/data")
    return parse_response(r)

# PUT	/devices/${DEVICE_ID}/endpoints/${DEVICE_ID}/data	Update tydom device data/state
@app.put("/devices/{id}/data")
async def put_devices_data(id, data: Data, tydom: Tydom=Depends(Tydom)):

    r = await send_message(tydom.socket, "PUT", f"/devices/{id}/endpoints/{id}/data", [data.__dict__])
    return parse_response(r)

#TODO
# PUT	/devices/${DEVICE_ID}/endpoints/${DEVICE_ID}/cdata?name=${CMD_NAME}	Run tydom device command


@app.on_event("shutdown")
async def shutdown_event():
    tydom = await socket_shutdown()