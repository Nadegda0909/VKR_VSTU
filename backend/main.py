from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
from backend.work_with_excel_rasp.downloader import *
import asyncio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


async def download_and_convert_schedule():
    yield {"event": "message", "data": "Скачивание файлов началось..."}
    await asyncio.to_thread(download_schedule_files, output_folder='work_with_excel_rasp/downloaded_files')
    yield {"event": "message", "data": "Файлы скачаны."}

    yield {"event": "message", "data": "Конвертация файлов началась..."}
    await asyncio.to_thread(convert_xls_to_xlsx, input_folder='work_with_excel_rasp/downloaded_files',
                            output_folder='work_with_excel_rasp/converted_files')
    yield {"event": "message", "data": "Файлы конвертированы."}

    yield {"event": "message", "data": "done"}


@app.get("/api/download_rasp")
async def download_rasp():
    return EventSourceResponse(download_and_convert_schedule())
