from fastapi import APIRouter,  Depends
from db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from product.schema import ProductCreateSchema, ProductOutSchema, ProductUpdateSchema
from product.crud import create_product, list_product, detail_product, delete_product, update_product

router = APIRouter()


@router.post('/create')
async def create_product_router(data: ProductCreateSchema, db: AsyncSession = Depends(get_db)):
    return await create_product(data, db)
 
@router.get(
    "/list"
    
)
async def list_product_router(
    db: AsyncSession = Depends(get_db)
):
    
    return await list_product(db)



@router.get("/detail/{id}")
async def detail_product_router(
    id:int,
    db: AsyncSession = Depends(get_db)
):
    
    return await detail_product(id, db)


@router.delete("/delete/{id}")
async def delete_product_router(
    id:int,
    db: AsyncSession = Depends(get_db)
):
    
    return await delete_product(id, db)


@router.patch("/update/{id}")
async def update_product_router(
    id:int,
    new_data: ProductUpdateSchema,
    db: AsyncSession = Depends(get_db)
):
    
    return await update_product(id, new_data, db)


