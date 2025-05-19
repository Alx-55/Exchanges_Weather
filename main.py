# РЕГИСТРАЦИЯ:
# from fastapi import FastAPI, Request, Form
# from fastapi.responses import HTMLResponse, RedirectResponse
# from fastapi.staticfiles import StaticFiles
# from fastapi.templating import Jinja2Templates
# from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
# from sqlalchemy import Column, Integer, String
# from sqlalchemy.orm import declarative_base
# from authx import AuthX
# import asyncio
#
# app = FastAPI()
#
# # HTML шаблоны
# templates = Jinja2Templates(directory="templates")
#
# # Подключение к базе данных
# DATABASE_URL = "sqlite+aiosqlite:///./users.db"
# engine = create_async_engine(DATABASE_URL, echo=True)
# async_session = async_sessionmaker(engine, expire_on_commit=False)
# Base = declarative_base()
#
# # Модель пользователя
#
#
# class User(Base):
#     __tablename__ = "users"
#     id = Column(Integer, primary_key=True)
#     username = Column(String, unique=True, index=True)
#     password = Column(String)
#
# # Инициализация AuthX (в упрощённом варианте)
# auth = AuthX()
#
#
# @app.on_event("startup")
# async def startup():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#
#
# @app.get("/", response_class=HTMLResponse)
# async def index():
#     return RedirectResponse("/register")
#
#
# @app.get("/register", response_class=HTMLResponse)
# async def register_form(request: Request):
#     return templates.TemplateResponse("register.html", {"request": request})
#
#
# @app.post("/register")
# async def register_user(username: str = Form(...), password: str = Form(...)):
#     async with async_session() as session:
#         async with session.begin():
#             user = User(username=username, password=auth.pwd_context.hash(password))
#             session.add(user)
#     return RedirectResponse(url="/register", status_code=303)





import os
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
import httpx

app = FastAPI()

templates = Jinja2Templates(directory="templates")

OPENWEATHER_API_KEY = "99e09229e133cd3639c708fe595a930b"  # Замени на свой ключ

cities = {
    "Киев": "Kyiv,UA",
    "Москва": "Moscow,RU",
    "Омск": "Omsk,RU",
    "Краснодар": "Krasnodar,RU",
    "Якутск": "Yakutsk,RU",
    "Хельсинки": "Helsinki,FI",
    "Калгари": "Calgary,CA",
    "Инсбург": "Innsbruck,AT",
    "Хабаровск": "Khabarovsk,RU"
}


async def fetch_usdt_uah():
    url = "https://api.binance.com/api/v3/ticker/price?symbol=USDTUAH"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        data = response.json()
        return float(data["price"])


async def fetch_weather(city: str):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={OPENWEATHER_API_KEY}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        data = response.json()
        return round(data["main"]["temp"], 1)


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("rate.html", {"request": request})


@app.get("/rate")
async def get_rate():
    try:
        rate = await fetch_usdt_uah()
        return JSONResponse(content={"rate": rate})
    except Exception:
        return JSONResponse(content={"rate": "Ошибка"}, status_code=500)


@app.get("/weather")
async def get_weather():
    try:
        temps = {}
        for name, query in cities.items():
            temp = await fetch_weather(query)
            temps[name] = temp
        return JSONResponse(content={"temps": temps})
    except Exception:
        return JSONResponse(content={"temps": {}, "error": "Ошибка загрузки"}, status_code=500)
