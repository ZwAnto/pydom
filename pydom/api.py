import os
from pathlib import Path
from pprint import pprint

import urllib3
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

import pydom
from pydom.routes import cozytouch, tydom

pprint(os.environ)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = FastAPI()

app.include_router(tydom.router)
app.include_router(cozytouch.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    pass


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(str(Path(pydom.__path__[0]) / "assets/favicon-196x196.png"))
