
from datetime import datetime

from fastapi import APIRouter, Depends, Request
from fastapi.responses import PlainTextResponse

from pydom.schemas.tydom import FileType, RootType, DeviceType, Data
from pydom.socket import Tydom, parse_response, send_message, socket_shutdown

router = APIRouter(prefix="/tydom")


@router.get('/metrics', response_class=PlainTextResponse)
async def metrics(tydom: Tydom=Depends(Tydom)):

    
    body = []

    r = await send_message(tydom.socket, "POST", "/refresh/all")
    r = await send_message(tydom.socket, "GET", "/devices/data")
    data = parse_response(r)

    try:
        for device in data['content']:
            for endpoint in device['endpoints']:
                for entry in endpoint['data']:
                    if entry['name'] in ['temperature', 'energyIndexTi1', 'energyTotIndexGas', 'energyIndexHeatGas', 'energyIndexECSGas', 'outTemperature', 'setpoint']:
                        body.append(f'{entry["name"]} {{device="{device["id"]}", entrypoint="{endpoint["id"]}"}} {entry["value"] if entry["value"] else 0} {int(datetime.now().timestamp())*1000}')
    except Exception:
        pass

    return '\n'.join(body) + '\n'


# protocols or info
@router.get("/{par}")
async def root(par: RootType, request: Request, tydom: Tydom=Depends(Tydom)):
    r = await send_message(tydom.socket, 'GET', request.scope['path'])
    return parse_response(r)

# /configs/file	Get tydom user config
# /groups/file	Get tydom groups config
# /moments/file	Get tydom moments config
# /scenarios/file	Get tydom scenarios config
@router.get("/{par}/file")
async def file(par: FileType, tydom: Tydom=Depends(Tydom)):
    r = await send_message(tydom.socket, "GET", f"/{par}/file")
    return parse_response(r)

# /devices/data	Get tydom devices data/state
# /devices/meta	Get tydom devices meta
# /devices/cmeta	Get tydom devices command meta
@router.get("/devices/{par}")
async def device(par: DeviceType, tydom: Tydom=Depends(Tydom)):
    r = await send_message(tydom.socket, 'GET', f"/devices/{par}")
    return parse_response(r)

# POST	/refresh/all	Force refresh tydom devices data
@router.post("/refresh/all")
async def refresh(tydom: Tydom=Depends(Tydom)):
    r = await send_message(tydom.socket, "POST", "/refresh/all")
    return parse_response(r)

# GET	/devices/${DEVICE_ID}/endpoints/${DEVICE_ID}/data	GET tydom device data/state
@router.get("/devices/{id}/data")
async def device_data(id, tydom: Tydom=Depends(Tydom)):
    r = await send_message(tydom.socket, "GET", f"/devices/{id}/endpoints/{id}/data")
    return parse_response(r)

# PUT	/devices/${DEVICE_ID}/endpoints/${DEVICE_ID}/data	Update tydom device data/state
@router.put("/devices/{id}/data")
async def put_devices_data(id, data: Data, tydom: Tydom=Depends(Tydom)):

    r = await send_message(tydom.socket, "PUT", f"/devices/{id}/endpoints/{id}/data", [data.__dict__])
    return parse_response(r)

#TODO
# PUT	/devices/${DEVICE_ID}/endpoints/${DEVICE_ID}/cdata?name=${CMD_NAME}	Run tydom device command


@router.on_event("shutdown")
async def shutdown_event():
    _ = await socket_shutdown()