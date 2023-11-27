
from datetime import datetime

from fastapi import APIRouter, Depends

from pydom.cozy_client import CozyTouchClient

router = APIRouter(prefix="/cozytouch")

client = CozyTouchClient()

@router.get('/metrics')
async def metrics(client: CozyTouchClient=Depends(client.check_session)):
        
    deviceURL = "modbuslink://1546-7191-2398/1#2"
    nameState = "core:ElectricEnergyConsumptionState"
    result = client.get_state(deviceURL, nameState)
    value = result['value']

    body = []
    body.append(f'{nameState} {{device="{deviceURL}"}} {value} {int(datetime.now().timestamp())*1000}')

    return '\n'.join(body) + '\n'



