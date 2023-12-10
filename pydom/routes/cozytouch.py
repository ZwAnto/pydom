
from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse

from pydom.cozy_client import CozyTouchClient

router = APIRouter(prefix="/cozytouch")

client = CozyTouchClient()

@router.get('/metrics', response_class=PlainTextResponse)
async def metrics(client: CozyTouchClient=Depends(client.check_session)):
        
    deviceURL = "modbuslink://1546-7191-2398/1#2"
    nameState = "core:ElectricEnergyConsumptionState"
    if client.is_available(deviceURL):
        result = client.get_state(deviceURL, nameState)
        value = result['value']

        body = []
        body.append(f'{nameState} {{device="{deviceURL}"}} {value} {int(datetime.now().timestamp())*1000}')

        return '\n'.join(body) + '\n'
    else:
        return ''



# _deviceURL = quote_plus(deviceURL)
# client.check_session()
# r = client.session.get("https://ha110-1.overkiz.com/enduser-mobile-web/enduserAPI/setup/devices")

# from pprint import pprint



# pprint([j['name'] for i in r.json() for j in i.get('states', [])])
# pprint([i['deviceURL'] for i in r.json()])

# r = client.session.get(f"https://ha110-1.overkiz.com/enduser-mobile-web/enduserAPI/setup/devices/{_deviceURL}")
# pprint(r.json())