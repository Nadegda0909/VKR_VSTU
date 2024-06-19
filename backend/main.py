from fastapi import FastAPI, HTTPException, Request, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
from backend.work_with_excel_rasp.downloader import *
import asyncio
import json
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SessionMiddleware, secret_key="!secret")

app.state.session_store = {}

class LoginRequest(BaseModel):
    username: str
    password: str

@app.get("/api/data")
def read_root():
    return {"message": "Тестовое сообщение!"}

@app.post("/api/button-click")
def button_click():
    print("Button was clicked")
    return {"status": "Button click received"}

@app.post("/api/login")
def login(request: LoginRequest):
    if request.username == "диплом" and request.password == "123":
        return {"status": "success"}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

async def download_and_convert_schedule(session_id: str):
    session = json.loads(app.state.session_store.get(session_id, '{}'))
    session['progress'] = 1
    app.state.session_store[session_id] = json.dumps(session)
    yield {"event": "message", "data": "Скачивание файлов началось..."}
    await asyncio.to_thread(download_schedule_files, output_folder='work_with_excel_rasp/downloaded_files')
    session['progress'] = 2
    app.state.session_store[session_id] = json.dumps(session)
    yield {"event": "message", "data": "Файлы скачаны."}

    yield {"event": "message", "data": "Конвертация файлов началась..."}
    await asyncio.to_thread(convert_xls_to_xlsx, input_folder='work_with_excel_rasp/downloaded_files',
                            output_folder='work_with_excel_rasp/converted_files')
    session['progress'] = 3
    app.state.session_store[session_id] = json.dumps(session)
    yield {"event": "message", "data": "Файлы конвертированы."}

    session['progress'] = 4
    app.state.session_store[session_id] = json.dumps(session)
    yield {"event": "message", "data": "done"}

@app.get("/api/download_rasp")
async def download_rasp(request: Request):
    session_id = request.cookies.get("session")
    if not session_id:
        session_id = str(uuid.uuid4())
        response = Response()
        response.set_cookie(key="session", value=session_id)
        app.state.session_store[session_id] = json.dumps({"progress": 0})
        return response
    return EventSourceResponse(download_and_convert_schedule(session_id))

@app.get("/api/progress")
def get_progress(request: Request):
    session_id = request.cookies.get("session")
    session = json.loads(app.state.session_store.get(session_id, '{}'))
    progress = session.get('progress', 0)
    return {"progress": progress}
