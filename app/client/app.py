from typing import Annotated

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastui import FastUI, AnyComponent, prebuilt_html, components as c
from fastui.components.display import DisplayLookup
from fastui.events import GoToEvent, BackEvent
from fastui.forms import fastui_form
from pydantic import BaseModel

app = FastAPI()


class User(BaseModel):
    id: int
    name: str


class AddUser(BaseModel):
    name: str


users = [User(id=1, name="Sergey"),
         User(id=2, name="Nadya")]


@app.get("/api/", response_model=FastUI, response_model_exclude_none=True)
def read_root() -> list[AnyComponent]:
    return [
        c.Page(
            components=[
                c.Table(data=users,
                        columns=[
                            DisplayLookup(field="id", on_click=GoToEvent(url="/user/{id}/")),
                            DisplayLookup(field="name")]
                        ),
                c.Button(text="Добавить пользователя", on_click=GoToEvent(url="/addUser"))
            ]
        )
    ]


@app.post("/api/user")
def add_user(form: Annotated[AddUser, fastui_form(AddUser)]):
    new_user = User(id=users[-1].id + 1, **form.model_dump())
    users.append(new_user)
    return [c.FireEvent(event=GoToEvent(url="/"))]


@app.get("/api/addUser", response_model=FastUI, response_model_exclude_none=True)
def add_user():
    return [
        c.Page(
            components=[
                c.ModelForm(
                    model=AddUser,
                    submit_url="/api/user"
                )
            ]
        )
    ]


@app.post("/api/deleteUser/{id}", response_model=FastUI, response_model_exclude_none=True)
def delete_user(id):
    users.pop(users.index(id))
    return [c.FireEvent(event=GoToEvent(url="/"))]


@app.get("/api/user/{user_id}/", response_model=FastUI, response_model_exclude_none=True)
def get_user(user_id: int):
    user = next(u for u in users if u.id == user_id)
    return [
        c.Page(
            components=[
                c.Link(components=[c.Text(text="Назад")], on_click=BackEvent()),
                c.Details(
                    data=user
                ),
                c.Button(text="Удалить пользователя", on_click=GoToEvent(url="/deleteUser/{id}"))
            ]
        )
    ]


@app.get('/{path:path}')
async def html_landing() -> HTMLResponse:
    """Simple HTML page which serves the React app, comes last as it matches all paths."""
    return HTMLResponse(prebuilt_html(title='FastUI Demo'))
