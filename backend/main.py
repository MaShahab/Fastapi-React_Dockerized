from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from tasks.routes import router as tasks_routes
from users.routes import router as users_routes
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache


tags_metadata = [
    {
        "name": "tasks",
        "description": "Operations related to task management",
        "externalDocs": {
            "description": "More about tasks",
            "url": "https://example.com/docs/tasks",
        },
    }
]


import redis.asyncio as redis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from core.config import settings   # your Pydantic Settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application startup")
    # FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")
    redis_client = redis.from_url(settings.REDIS_URL, encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis_client), prefix="fastapi-cache")
    yield
    print("Application shutdown")


app = FastAPI(
    title="Project name",
    description="This a sections for describe project",
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Mahdi Shahabedin",
        "url": "https://www.mshahabedin.ir",
        "email": "mahshahab@gmail.com",
    },
    license_info={
        "name": "MIT",
    },
    lifespan=lifespan,
    openapi_tags=tags_metadata,
)

app.include_router(tasks_routes)
app.include_router(users_routes)

app.add_middleware(GZipMiddleware, minimum_size=1000)


from auth.basic_auth import get_authenticated_user
from users.models import UserModel



@app.get("/", status_code=200)
def public_route():
    return {"message": "This is a public route."}


# @app.get("/public")
# def public_route():
#     return {"message": "This is a public route."}

# @app.get("/private")
# def private_route(user: UserModel = Depends(get_authenticated_user)):
#     print(user)
#     return {"message": "This is a private route."}


# #########################################################################################################################
# #apikeyheader

# from fastapi import Security
# from auth.key_auth import get_api_key

# # A protected route
# @app.get("/private_apikey")
# async def protected_route(api_key: str = Security(get_api_key)):
#     return {"message": "You are authorized", "api_key_used": api_key}


# ####################################################################################

# from fastapi import Security
# from auth.query_auth import get_api_query
# @app.get("/private_apiquery")
# async def secure_data(api_key: str = Security(get_api_query)):
#     return {"message": "You are authorized!", "api_key_used": api_key}


####################################################################################

# from fastapi.security import OAuth2PasswordRequestForm
# from sqlalchemy.orm import Session
# from core.database import get_db
# from fastapi import status, HTTPException
# from users.models import TokenModel, UserModel
# from auth.token_auth import get_current_user, generate_token
# from datetime import *

# @app.post("/token")
# def login(form_data: OAuth2PasswordRequestForm = Depends(), db:Session = Depends(get_db)):
#     user = db.query(UserModel).filter(UserModel.username == form_data.username).first()
#     if not user or not user.verify_password(form_data.password):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )

#     # تولید توکن و زمان انقضای آن
#     expiration = datetime.utcnow() + timedelta(hours=1)  # توکن 1 ساعت اعتبار دارد
#     gen_token = generate_token(32)
#     new_token = TokenModel(token=gen_token, expiration=expiration, user_id=user.id)

#     db.add(new_token)
#     db.commit()
#     db.refresh(new_token)

#     return new_token

# @app.get("/private")
# def private_route(current_user: UserModel = Depends(get_current_user)):
#     return {"message": f"Hello {current_user.username}, this is a private route."}

# @app.get("/public")
# def public_route():
#     return {"message": "This is a public route."}

# from fastapi.security import OAuth2PasswordBearer
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="fdsfd")
# @app.get("/test")
# def test_route(token: str = Depends(oauth2_scheme), db:Session = Depends(get_db)):
#     print(token)


#############################################################################################

from auth.jwt_auth import (
    generate_access_token,
    generate_refresh_token,
    get_authenticated_user,
    decode_refresh_token,
)
from users.schemas import UserLoginSchema, UserRefreshTokenSchema
from sqlalchemy.orm import Session
from core.database import get_db
from fastapi import Depends, HTTPException, status
from fastapi.responses import JSONResponse


@app.post("/login")
async def user_login(request: UserLoginSchema, db: Session = Depends(get_db)):
    user_obj = db.query(UserModel).filter_by(username=request.username.lower()).first()
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="user doesnt exists"
        )
    if not user_obj.verify_password(request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="password is invalid"
        )

    access_token = generate_access_token(user_obj.id)
    refresh_token = generate_refresh_token(user_obj.id)
    return JSONResponse(
        content={
            "detail": "logged in successfully",
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
    )


@app.get("/private")
def private_route(user=Depends(get_authenticated_user)):
    print(user)
    return {"message": "this is a jwt private route."}


@app.post("/refresh_token")
async def user_refresh_token(
    request: UserRefreshTokenSchema, db: Session = Depends(get_db)
):
    user_id = decode_refresh_token(request.token)
    access_token = generate_access_token(user_id)
    return JSONResponse(content={"access_token": access_token})


from fastapi import Response, Request


@app.get("/get-cookie")
async def get_cookie(request: Request):
    print(request.__dict__)
    return {"message": "Cookie has been set successfully"}


@app.post("/set-cookie")
async def set_cookie(response: Response):
    response.set_cookie(key="name", value="mahdi")
    return {"message": "Cookie has been set!"}


@app.delete("/delete-cookie")
async def delete_cookie(response: Response):
    response.delete_cookie(key="name")
    return {"message": "Cookie has been deleted!"}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # اجازه به همه دامنه‌ها (برای محیط توسعه)
    allow_credentials=True,
    allow_methods=["*"],  # اجازه به همه متدها (GET, POST, PUT, DELETE و ...)
    allow_headers=["*"],  # اجازه به همه هدرها
)

from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    error_response = {
        "error" : True,
        "status_code": exc.status_code,
        "detail": str(exc.detail)
    }

    return JSONResponse(status_code= exc.status_code, content=error_response)

@app.exception_handler(RequestValidationError)
async def http_validation_exception_handler(request, exc):
    error_response = {
        "error" : True,
        "status_code": exc.status_code,
        "detail": "There was a problem with your from request",
        "content": exc.errors()
    }

    return JSONResponse(status_code= exc.status_code, content=error_response)

import time
from fastapi import BackgroundTasks


def task_management():
    print("start task")
    print("doing the process")
    time.sleep(10)
    print("finished task")

@app.get("/initiate_task", status_code=200)
async def initiate_task(background_tasks: BackgroundTasks):
    background_tasks.add_task(task_management)
    print("Task is done")
    return JSONResponse(content={"message":"Task is done"})


from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache
import httpx

cache_backend = InMemoryBackend()
FastAPICache.init(cache_backend)

async def request_current_weather(latitude: float, longitude: float):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m, relative_humidity_2m"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        current_weather = data.get("current", {})
        return current_weather
    else:
        return None

@app.get("/fetch-current-weather", status_code=200)
async def fetch_current_weather(latitude: float = 40.7128, longitude: float = -74.0060):
    current_weather = await request_current_weather(latitude, longitude)
    print(current_weather)
    # if current_weather:
    #     return JSONResponse(content={"current_weather": current_weather})
    # else:
    #     return JSONResponse(content={"detail": "Failed to refresh weather"}, status_code=500)

# Cached endpoint




@app.get("/hello")
@cache(expire=20)  # cache response for 10 seconds
async def test():
    print("👉 Executing handler (not cached)")  # to show when cache is bypassed
    return {"message": f"Hello world"}



@app.get("/pokemon/{name}")
@cache(expire=60)  # cache result for 60 seconds
async def get_pokemon(name: str):
    """
    Fetch data from the PokeAPI (https://pokeapi.co/), cache in Redis for 60s.
    """
    print(f"Fetching {name} from external API...")  # runs only on cache miss
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://pokeapi.co/api/v2/pokemon/{name}")
        response.raise_for_status()
        return response.json()
    

# from fastapi import FastAPI
# from fastapi_cache import FastAPICache
# from fastapi_cache.backends.redis import RedisBackend
# from fastapi_cache.decorator import cache
# import redis.asyncio as redis
# import httpx

# app = FastAPI()


# @app.on_event("startup")
# async def on_startup():
#     redis_client = redis.from_url("redis://redis:6379/0")
#     try:
#         pong = await redis_client.ping()
#         print("✅ Connected to Redis:", pong)
#     except Exception as e:
#         print("❌ Redis connection failed:", e)

#     FastAPICache.init(RedisBackend(redis_client), prefix="fastapi-cache")


# @app.get("/pokemon/{name}")
# @cache(expire=60)  # cached for 60s
# async def get_pokemon(name: str):
#     print(f"Fetching {name} from external API...")  # shown only on cache miss
#     async with httpx.AsyncClient() as client:
#         response = await client.get(f"https://pokeapi.co/api/v2/pokemon/{name}")
#         response.raise_for_status()
#         return response.json()

from core.email_util import send_mail

@app.get("/test-send-mail", status_code=200)
async def test_send_mail():
    await send_mail(
        subject="Test Email from FastAPI",
        recipients=["mahshahab@gmail.com"],
        body="This is a test email sent using the email_util function."
    )
    return JSONResponse(content={"detail":"Email has been sent"})


# from core.celery_conf import add_number

# @app.get('/celery_add_number_task', status_code=200)
# async def celery_add_number_task():
#     add_number.delay(1,2)
#     return JSONResponse(content={"detail":"task is done"})


from core.celery_tasks import add  # <-- import from inner core
from celery.result import AsyncResult

app = FastAPI()

@app.get("/add/")
def call_add(x: int, y: int):
    task = add.delay(x, y)
    return {"task_id": task.id, "status": "submitted"}

@app.get("/check-celery-task-result", status_code=200)
async def initiate_celery_task(task_id:str):
    result = AsyncResult(task_id).ready()
    return JSONResponse(content={"result":result})

