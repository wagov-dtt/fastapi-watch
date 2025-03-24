from fastapi import FastAPI, Request, status, BackgroundTasks
import os, json, requests

app = FastAPI()

ORIGIN_URL = f"https://{os.environ['ORIGIN_FQDN']}/{os.environ['ORIGIN_PATH']}"

async def log_request(request: Request, body):
    requester = requests.get(ORIGIN_URL).json()
    logdata = {
        "method": request.method,
        "headers": request.headers,
        "url": request.url,
        "body": body,
        "requester": requester
    }
    print(logdata)

@app.api_route("/{path:path}", methods=("DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"))
async def catch_all(request: Request, background_tasks: BackgroundTasks, path: str = ""):
    try:
        try:
            body = await request.json()
        except:
            body = await request.body()
    except:
        body = ""
    background_tasks.add_task(log_request, request, body)
    return status.HTTP_202_ACCEPTED