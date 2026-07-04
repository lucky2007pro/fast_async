from product.models import Product
from product.schema import ProductCreateSchema, ProductOutSchema, ProductUpdateSchema
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.exceptions import HTTPException
from fastapi import status
from sqlalchemy import select


async def create_product(data: ProductCreateSchema, db: AsyncSession):
    product = Product(**data.model_dump())
    
    db.add(product)
    
    await db.commit()
    await db.refresh(product)
    
    return {
        'msg': 'Product created',
        'status': status.HTTP_201_CREATED,
        'data': ProductOutSchema.model_validate(product)
    }


async def list_product(db: AsyncSession):

    
    
    query = select(Product) 
    
    result = await db.execute(query)
    
    products = result.scalars().all()
    
    
    return {
        'msg': 'Products',
        'count': len(products),
        'status':status.HTTP_200_OK,
        'data': products
        }


async def detail_product(id:int, db:AsyncSession):
    # result = await db.get(Product, id)
    
    query = select(Product).where(
        Product.id == id
    )

    result = await db.execute(query)

    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product topilmadi"
        )

    return product


async def delete_product(id:int, db:AsyncSession):
    product = await db.get(Product, id)
    

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product topilmadi"
        )
        
    await db.delete(product)
    await db.commit()

    return {
        'msg': 'Product deleted',
        'status':status.HTTP_204_NO_CONTENT
        }
    
async def update_product(id:int, new_data: ProductUpdateSchema, db:AsyncSession):
    product = await db.get(Product, id)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product topilmadi"
        )
        
    data = new_data.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(product, key, value)
        
    
    await db.commit()
    await db.refresh(product)
    
    return {
        'msg': 'Product updated',
        'status':status.HTTP_200_OK,
        'data': ProductOutSchema.model_validate(product)
        }