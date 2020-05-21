from fastapi import FastAPI
from api import router
from starlette.middleware.cors import CORSMiddleware
from uvicorn import run
app = FastAPI()


# 设置跨域
origins = [
    '*'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,  # Credentials (Authorization headers, Cookies, etc)
    allow_methods=["*"],     # Specific HTTP methods (POST, PUT) or all of them with the wildcard "*".
    allow_headers=["*"],     # Specific HTTP headers or all of them with the wildcard "*".
)
app.include_router(router,prefix='/api/private/v1')

if __name__ == '__main__':
    run(app,port=3000)