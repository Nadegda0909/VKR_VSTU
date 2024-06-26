from fastapi import FastAPI, HTTPException, UploadFile, File, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
import os
import shutil
import asyncio
import json
import uuid
from backend.work_with_excel_rasp.downloader import *
from backend.work_with_excel_rasp.parser import run as run_parser_from_file
from backend.work_with_excel_groups.group_parser import run as run_group_parser_from_file
from backend.work_with_excel_groups.group_maker import run as run_group_maker_vstu_from_file
from backend.work_with_excel_groups.group_maker_for_others import run as run_group_maker_for_others_from_file
from backend.work_with_ck_excel_rasp.rasp_ck_creator import run as run_ck_rasp_creator_from_file
from backend.work_with_ck_excel_rasp.groups_ck_creator import run as run_ck_groups_creator_from_file

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


async def upload_file_progress(session_id: str):
    session = json.loads(app.state.session_store.get(session_id, '{}'))
    session['progress_upload'] = 1
    app.state.session_store[session_id] = json.dumps(session)
    yield {"event": "message", "data": "Файл загружается"}

    await asyncio.sleep(2)  # Замените это реальной логикой загрузки файла

    session['progress_upload'] = 2
    app.state.session_store[session_id] = json.dumps(session)
    yield {"event": "message", "data": "Файл загружен"}


@app.post("/api/upload")
async def upload_file(request: Request, file: UploadFile = File(...)):
    session_id = request.cookies.get("session")
    if not session_id:
        session_id = str(uuid.uuid4())
        response = Response()
        response.set_cookie(key="session", value=session_id)
        app.state.session_store[session_id] = json.dumps({"progress_upload": 0})
        return response

    upload_folder = 'work_with_excel_groups'
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return EventSourceResponse(upload_file_progress(session_id))


@app.get("/api/upload_progress")
async def get_upload_progress(request: Request):
    session_id = request.cookies.get("session")
    if not session_id:
        return {"progress": 0}
    return EventSourceResponse(upload_file_progress(session_id))


@app.get("/api/progress_upload")
def get_progress_upload(request: Request):
    session_id = request.cookies.get("session")
    if not session_id:
        return {"progress": 0}
    session = json.loads(app.state.session_store.get(session_id, '{}'))
    progress = session.get('progress_upload', 0)
    return {"progress": progress}


def delete_dirs_in_path(path: str):
    items = os.listdir(path=path)
    folders = [item for item in items if os.path.isdir(os.path.join(path, item)) and "__" not in item]
    for folder in folders:
        folder_path = os.path.join(path, folder)
        try:
            shutil.rmtree(folder_path)
            print(f'{Fore.GREEN}Папка {folder_path} успешно удалена{Style.RESET_ALL}')
        except OSError as e:
            print(f'{Fore.RED}Ошибка при удалении папки {folder_path}: {e}{Style.RESET_ALL}')


async def download_and_convert_schedule(session_id: str):
    await asyncio.to_thread(delete_dirs_in_path, path='work_with_excel_rasp')
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
        response = Response(content=json.dumps({"status": "new session"}), media_type="application/json")
        response.set_cookie(key="session", value=session_id)
        app.state.session_store[session_id] = json.dumps({"progress": 0})
        return response
    return EventSourceResponse(download_and_convert_schedule(session_id))


@app.get("/api/progress")
def get_progress(request: Request):
    session_id = request.cookies.get("session")
    if not session_id:
        return {"progress": 0}
    session = json.loads(app.state.session_store.get(session_id, '{}'))
    progress = session.get('progress', 0)
    return {"progress": progress}


async def run_parser(session_id: str):
    session = json.loads(app.state.session_store.get(session_id, '{}'))
    session['parser_progress'] = 1
    app.state.session_store[session_id] = json.dumps(session)
    yield {"event": "message", "data": "Запуск парсера..."}

    await asyncio.to_thread(run_parser_from_file, path_to_excel_files='work_with_excel_rasp/converted_files')

    session['parser_progress'] = 4
    app.state.session_store[session_id] = json.dumps(session)
    yield {"event": "message", "data": "Парсер успешно завершен."}


@app.get("/api/run_parser")
async def run_parser_endpoint(request: Request):
    session_id = request.cookies.get("session")
    if not session_id:
        session_id = str(uuid.uuid4())
        response = Response()
        response.set_cookie(key="session", value=session_id)
        app.state.session_store[session_id] = json.dumps({"parser_progress": 0})
        return response
    return EventSourceResponse(run_parser(session_id))


@app.get("/api/parser_progress")
def get_parser_progress(request: Request):
    session_id = request.cookies.get("session")
    session = json.loads(app.state.session_store.get(session_id, '{}'))
    progress = session.get('parser_progress', 0)
    return {"parser_progress": progress}


async def run_group_parser(session_id: str):
    session = json.loads(app.state.session_store.get(session_id, '{}'))
    session['group_parser_progress'] = 1
    app.state.session_store[session_id] = json.dumps(session)
    yield {"event": "message", "data": "Запуск парсера для групп..."}

    await asyncio.to_thread(run_group_parser_from_file, path='work_with_excel_groups')

    session['group_parser_progress'] = 4
    app.state.session_store[session_id] = json.dumps(session)
    yield {"event": "message", "data": "Парсер успешно завершен."}


@app.get("/api/run_group_parser")
async def run_group_parser_endpoint(request: Request):
    session_id = request.cookies.get("session")
    if not session_id:
        session_id = str(uuid.uuid4())
        response = Response()
        response.set_cookie(key="session", value=session_id)
        app.state.session_store[session_id] = json.dumps({"group_parser_progress": 0})
        return response
    return EventSourceResponse(run_group_parser(session_id))


@app.get("/api/group_parser_progress")
def get_group_parser_progress(request: Request):
    session_id = request.cookies.get("session")
    session = json.loads(app.state.session_store.get(session_id, '{}'))
    progress = session.get('group_parser_progress', 0)
    return {"group_parser_progress": progress}


async def run_group_maker_vstu(session_id: str):
    session = json.loads(app.state.session_store.get(session_id, '{}'))
    session['group_maker_vstu_progress'] = 1
    app.state.session_store[session_id] = json.dumps(session)
    yield {"event": "message", "data": "Создаются группы и расписание для ВолгГТУ..."}

    await asyncio.to_thread(run_group_maker_vstu_from_file)
    await asyncio.to_thread(run_group_maker_for_others_from_file)

    session['group_maker_vstu_progress'] = 4
    app.state.session_store[session_id] = json.dumps(session)
    yield {"event": "message", "data": "Группы и расписание для ВолгГТУ созданы."}


@app.get("/api/run_group_maker_vstu")
async def run_group_maker_vstu_endpoint(request: Request):
    session_id = request.cookies.get("session")
    if not session_id:
        session_id = str(uuid.uuid4())
        response = Response()
        response.set_cookie(key="session", value=session_id)
        app.state.session_store[session_id] = json.dumps({"group_maker_vstu_progress": 0})
        return response
    return EventSourceResponse(run_group_maker_vstu(session_id))


@app.get("/api/group_maker_vstu_progress")
def get_group_maker_vstu_progress(request: Request):
    session_id = request.cookies.get("session")
    session = json.loads(app.state.session_store.get(session_id, '{}'))
    progress = session.get('group_maker_vstu_progress', 0)
    return {"group_maker_vstu_progress": progress}


async def run_group_maker_for_others(session_id: str):
    session = json.loads(app.state.session_store.get(session_id, '{}'))
    session['group_maker_for_others_progress'] = 1
    app.state.session_store[session_id] = json.dumps(session)
    yield {"event": "message", "data": "Создаются группы и расписание для ВолгГТУ..."}

    await asyncio.to_thread(run_group_maker_for_others_from_file)

    session['group_maker_for_others_progress'] = 4
    app.state.session_store[session_id] = json.dumps(session)
    yield {"event": "message", "data": "Группы и расписание для ВолгГТУ созданы."}


@app.get("/api/run_group_maker_for_others")
async def run_group_maker_for_others_endpoint(request: Request):
    session_id = request.cookies.get("session")
    if not session_id:
        session_id = str(uuid.uuid4())
        response = Response()
        response.set_cookie(key="session", value=session_id)
        app.state.session_store[session_id] = json.dumps({"group_maker_for_others_progress": 0})
        return response
    return EventSourceResponse(run_group_maker_for_others(session_id))


@app.get("/api/group_maker_for_others_progress")
def get_group_maker_for_others_progress(request: Request):
    session_id = request.cookies.get("session")
    session = json.loads(app.state.session_store.get(session_id, '{}'))
    progress = session.get('group_maker_for_others_progress', 0)
    return {"group_maker_for_others_progress": progress}


async def run_ck_excel_rasp(session_id: str):
    session = json.loads(app.state.session_store.get(session_id, '{}'))
    session['ck_excel_rasp_progress'] = 1
    app.state.session_store[session_id] = json.dumps(session)
    yield {"event": "message", "data": "Создается Excel-файл с расписанием..."}

    await asyncio.to_thread(run_ck_rasp_creator_from_file, path='work_with_ck_excel_rasp/')

    session['ck_excel_rasp_progress'] = 4
    app.state.session_store[session_id] = json.dumps(session)
    yield {"event": "message", "data": "Excel-файл с расписанием создан."}


@app.get("/api/run_ck_excel_rasp")
async def run_ck_excel_rasp_endpoint(request: Request):
    session_id = request.cookies.get("session")
    if not session_id:
        session_id = str(uuid.uuid4())
        response = Response()
        response.set_cookie(key="session", value=session_id)
        app.state.session_store[session_id] = json.dumps({"ck_excel_rasp_progress": 0})
        return response
    return EventSourceResponse(run_ck_excel_rasp(session_id))


@app.get("/api/ck_excel_rasp_progress")
def get_ck_excel_rasp_progress(request: Request):
    session_id = request.cookies.get("session")
    session = json.loads(app.state.session_store.get(session_id, '{}'))
    progress = session.get('ck_excel_rasp_progress', 0)
    return {"ck_excel_rasp_progress": progress}


async def run_ck_excel_group(session_id: str):
    session = json.loads(app.state.session_store.get(session_id, '{}'))
    session['ck_excel_group_progress'] = 1
    app.state.session_store[session_id] = json.dumps(session)
    yield {"event": "message", "data": "Создается Excel-файл со списком групп..."}

    await asyncio.to_thread(run_ck_groups_creator_from_file, path='work_with_ck_excel_rasp/')

    session['ck_excel_group_progress'] = 4
    app.state.session_store[session_id] = json.dumps(session)
    yield {"event": "message", "data": "Excel-файл со списком групп создан."}


@app.get("/api/run_ck_excel_group")
async def run_ck_excel_group_endpoint(request: Request):
    session_id = request.cookies.get("session")
    if not session_id:
        session_id = str(uuid.uuid4())
        response = Response()
        response.set_cookie(key="session", value=session_id)
        app.state.session_store[session_id] = json.dumps({"ck_excel_group_progress": 0})
        return response
    return EventSourceResponse(run_ck_excel_group(session_id))


@app.get("/api/ck_excel_group_progress")
def get_ck_excel_group_progress(request: Request):
    session_id = request.cookies.get("session")
    session = json.loads(app.state.session_store.get(session_id, '{}'))
    progress = session.get('ck_excel_group_progress', 0)
    return {"ck_excel_group_progress": progress}


@app.get("/api/download_file")
def download_file():
    file_path = "work_with_ck_excel_rasp/schedule_ck.xlsx"  # Путь к файлу на сервере
    return FileResponse(path=file_path, filename="schedule_ck.xlsx", media_type='application/octet-stream')


@app.get("/api/download_group_file")
def download_file():
    file_path = "work_with_ck_excel_rasp/group_ck.xlsx"  # Путь к файлу на сервере
    return FileResponse(path=file_path, filename="group_ck.xlsx", media_type='application/octet-stream')


async def run_create_only_rasp_for_vstu(session_id: str):
    session = json.loads(app.state.session_store.get(session_id, '{}'))
    session['create_only_rasp_for_vstu_progress'] = 1
    app.state.session_store[session_id] = json.dumps(session)
    yield {"event": "message", "data": "Создается только расписание для ВолгГТУ..."}

    # await asyncio.to_thread(run_create_only_rasp_for_vstu_from_file)
    time.sleep(1)
    session['create_only_rasp_for_vstu_progress'] = 4
    app.state.session_store[session_id] = json.dumps(session)
    yield {"event": "message", "data": "Расписание для ВолгГТУ создано."}


@app.get("/api/run_create_only_rasp_for_vstu")
async def run_create_only_rasp_for_vstu_endpoint(request: Request):
    session_id = request.cookies.get("session")
    if not session_id:
        session_id = str(uuid.uuid4())
        response = Response()
        response.set_cookie(key="session", value=session_id)
        app.state.session_store[session_id] = json.dumps({"create_only_rasp_for_vstu_progress": 0})
        return response
    return EventSourceResponse(run_create_only_rasp_for_vstu(session_id))


@app.get("/api/create_only_rasp_for_vstu_progress")
def get_create_only_rasp_for_vstu_progress(request: Request):
    session_id = request.cookies.get("session")
    session = json.loads(app.state.session_store.get(session_id, '{}'))
    progress = session.get('create_only_rasp_for_vstu_progress', 0)
    return {"create_only_rasp_for_vstu_progress": progress}


async def run_create_only_rasp_for_others(session_id: str):
    session = json.loads(app.state.session_store.get(session_id, '{}'))
    session['create_only_rasp_for_others_progress'] = 1
    app.state.session_store[session_id] = json.dumps(session)
    yield {"event": "message", "data": "Создаются только расписание для остальных..."}

    # await asyncio.to_thread(run_create_only_rasp_for_others_from_file)
    time.sleep(1)
    session['create_only_rasp_for_others_progress'] = 4
    app.state.session_store[session_id] = json.dumps(session)
    yield {"event": "message", "data": "Расписание для остальных создано."}


@app.get("/api/run_create_only_rasp_for_others")
async def run_create_only_rasp_for_others_endpoint(request: Request):
    session_id = request.cookies.get("session")
    if not session_id:
        session_id = str(uuid.uuid4())
        response = Response()
        response.set_cookie(key="session", value=session_id)
        app.state.session_store[session_id] = json.dumps({"create_only_rasp_for_others_progress": 0})
        return response
    return EventSourceResponse(run_create_only_rasp_for_others(session_id))


@app.get("/api/create_only_rasp_for_others_progress")
def get_create_only_rasp_for_others_progress(request: Request):
    session_id = request.cookies.get("session")
    session = json.loads(app.state.session_store.get(session_id, '{}'))
    progress = session.get('create_only_rasp_for_others_progress', 0)
    return {"create_only_rasp_for_others_progress": progress}