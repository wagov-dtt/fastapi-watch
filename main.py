from fastapi import FastAPI, Request, status, BackgroundTasks
import os, json, sys
from hishel import AsyncCacheClient, AsyncInMemoryStorage
from httpx import Limits
from datetime import datetime, timezone

app = FastAPI()
client = AsyncCacheClient(
    limits=Limits(max_connections=1000), storage=AsyncInMemoryStorage()
)

app = FastAPI()

ORIGIN_URL = f"{os.environ['ORIGIN_BASE']}/{os.environ['ORIGIN_PATH']}"


@app.get("/traefik_dynamic_conf.json")
async def traefik_config(request: Request):
    return {
        "http": {
            "middlewares": {
                "forward-auth": {
                    "forwardAuth": {
                        "address": str(request.url_for("audit")),
                        "forwardBody": True,
                        "trustForwardHeader": True,
                    }
                }
            },
            "routers": {
                "passthrough": {
                    # Can restrict by headers e.g. "rule": "Header(`X-CDN-token`, `secret`) && PathPrefix(`/`)",
                    "rule": "PathPrefix(`/`)",
                    "entryPoints": ["web"],
                    "middlewares": ["forward-auth"],
                    "service": "backend",
                }
            },
            "services": {
                "backend": {
                    "loadBalancer": {"servers": [{"url": os.environ['ORIGIN_BASE']}]}
                }
            },
        },
    }


async def body_to_string(request: Request):
    try:
        try:
            body = await request.json()
        except:
            body = await request.body()
    except:
        body = ""
    return str(body)


async def log_request(request: Request, body):
    try:
        response = await client.get(ORIGIN_URL, headers=request.headers)
        requester = response.json()
    except Exception as e:
        requester = {"origin_url": ORIGIN_URL, "error": str(e)}
    logdata = {
        "start_time": request.state.start_time,
        "headers": dict(request.headers),
        "body": body,
        "requester": requester,
    }
    json.dump(logdata, sys.stdout)
    sys.stdout.write("\n")

@app.get("/mock_auth")
async def mock_auth(request: Request, identity: str = "mock-userid"):
    userinfo = {
        "identity": identity,
        "access": "allowed",
        "auth-backend": "mock-identity-provider"
    }
    return userinfo
    

@app.get("/audit")
async def audit(request: Request, tasks: BackgroundTasks):
    request.state.start_time = datetime.now(timezone.utc).isoformat()
    body = await body_to_string(request)
    tasks.add_task(log_request, request, body)
    return status.HTTP_202_ACCEPTED
