from fastapi import FastAPI
from product.router import router as product_router
from user.auth_router import router as user_router


app = FastAPI()

app.include_router(product_router, prefix='/product', tags=['Product'])
app.include_router(user_router, prefix='/auth', tags=['Auth'])