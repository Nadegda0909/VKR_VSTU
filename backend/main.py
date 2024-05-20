from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/data")
def read_root():
    return {"message": "Я не панк"}


@app.post("/api/button-click")
def button_click():
    print("Button was clicked")
    return {"status": "Button click received"}
