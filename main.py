
import os
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
import httpx
from fastapi.staticfiles import StaticFiles  # подключаем static/
from fastapi.responses import RedirectResponse


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")  # подключаем static/

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
    "Хабаровск": "Khabarovsk,RU",
    "Пермь": "Perm,RU",
    "Иркутск": "Irkutsk,RU"
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


@app.get("/image")
async def show_image(request: Request, name: str):
    # name — это например Binance.png или Москва.jpg
    image_url = f"/static/{name}"
    return templates.TemplateResponse("image.html", {
        "request": request,
        "image_url": image_url,
        "title": name.split('.')[0]
    })

