from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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
    return {"message": "Я не панк"}


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
