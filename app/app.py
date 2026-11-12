from fastapi import FastAPI, Depends, HTTPException, status,Query
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from app import schema
from app.schema import ProductCreate,ProductResponse,ProductUpdate,StockRestock,StockCorrection

from typing import Literal
from fastapi import UploadFile, File
from app.imagekit_client import imagekit

from app.database import Base, engine, get_db
from app import models




@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield



app = FastAPI(lifespan=lifespan)



@app.get("/")
def home():
    return {"message": "Welcome to MiniMart API!"}




@app.get("/products", response_model=list[ProductResponse])
def get_products(
    search: str | None = Query(default=None),
    category: str | None = Query(default=None),
    min_price: float | None = Query(default=None, ge=0),
    max_price: float | None = Query(default=None, ge=0),

    is_active: bool = Query(default=True),

    sort_by: Literal["id", "name", "price", "created_at"] = Query(default="id"),
    sort_order: Literal["asc", "desc"] = Query(default="asc"),

    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),

    db: Session = Depends(get_db)
):
    query = db.query(models.Product)

    # Validate price range
    if (
        min_price is not None
        and max_price is not None
        and min_price > max_price
    ):
        raise HTTPException(
            status_code=422,
            detail="Minimum price cannot be greater than maximum price"
        )

    # Filter by active status
    query = query.filter(
        models.Product.is_active == is_active
    )

    # Search by product name
    if search:
        query = query.filter(
            models.Product.name.ilike(f"%{search}%")
        )

    # Filter by category
    if category:
        query = query.filter(
            models.Product.category.ilike(category)
        )

    # Filter by minimum price
    if min_price is not None:
        query = query.filter(
            models.Product.price >= min_price
        )

    # Filter by maximum price
    if max_price is not None:
        query = query.filter(
            models.Product.price <= max_price
        )

    # Sorting
    sort_column = getattr(models.Product, sort_by)

    if sort_order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    # Pagination
    products = query.offset(skip).limit(limit).all()

    return products



# GET ONE PRODUCT

@app.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(
        models.Product.id == product_id,
        models.Product.is_active == True
    ).first()

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return product




# CREATE PRODUCT
@app.post(
    "/products",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED
)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db)
):
    new_product = models.Product(**product.model_dump())

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product




@app.post("/products/{product_id}/image")
def upload_product_image(
    product_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Find the product
    product = db.query(models.Product).filter(
        models.Product.id == product_id
    ).first()

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    # Validate image type
    allowed_types = [
        "image/jpeg",
        "image/png",
        "image/webp"
    ]

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Only JPEG, PNG, and WEBP images are allowed"
        )

    # Read image data (maximum 5 MB)
    image_data = file.file.read(5 * 1024 * 1024 + 1)

    if not image_data:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty"
        )

    if len(image_data) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="Image size must not exceed 5 MB"
        )

    # Upload image to ImageKit
    try:
        upload_result = imagekit.files.upload(
            file=image_data,
            file_name=f"product-{product_id}-{file.filename}",
            folder="/products"
        )

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="Image upload failed"
        ) from exc

    # Save ImageKit URL in PostgreSQL
    product.image_url = upload_result.url

    db.commit()
    db.refresh(product)

    return {
        "message": "Product image uploaded successfully",
        "image_url": product.image_url
    }




@app.post(
    "/products/bulk",
    response_model=list[schema.ProductResponse],
    status_code=201
)
def create_products_bulk(
    products: list[schema.ProductCreate],
    db: Session = Depends(get_db)
):
    if not products:
        raise HTTPException(
            status_code=400,
            detail="Product list cannot be empty"
        )

    new_products = [
        models.Product(**product.model_dump())
        for product in products
    ]

    db.add_all(new_products)
    db.commit()

    for product in new_products:
        db.refresh(product)

    return new_products




@app.post(
    "/products/{product_id}/restock",
    response_model=ProductResponse
)
def restock_product(
    product_id: int,
    stock_data: StockRestock,
    db: Session = Depends(get_db)
):
    product = db.query(models.Product).filter(
        models.Product.id == product_id
    ).first()

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    product.stock_quantity += stock_data.quantity

    db.commit()
    db.refresh(product)

    return product


# the lesson you are giving me less and when i chat repetdly its quickly finished so i want 3 times of  lessons that you are giving me right now and we can track  easily

@app.get(
    "/inventory/low-stock",
    response_model=list[ProductResponse]
)
def get_low_stock_products(
    threshold: int = Query(default=10, ge=0),
    db: Session = Depends(get_db)
):
    products = db.query(models.Product).filter(
        models.Product.is_active.is_(True),
        models.Product.stock_quantity <= threshold
    ).order_by(
        models.Product.stock_quantity.asc()
    ).all()

    return products




@app.put("/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    updated_product: ProductCreate,
    db: Session = Depends(get_db)
):
    product = db.query(models.Product).filter(
        models.Product.id == product_id
    ).first()

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    for key, value in updated_product.model_dump().items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)

    return product




@app.patch("/products/{product_id}", response_model=ProductResponse)
def patch_product(
    product_id: int,
    updated_data: ProductUpdate,
    db: Session = Depends(get_db)
):
    
    product = db.query(models.Product).filter(
        models.Product.id == product_id
    ).first()

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    update_data = updated_data.model_dump(exclude_unset=True)


    for key, value in update_data.items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)

    return product



@app.patch(
    "/products/{product_id}/stock",
    response_model=ProductResponse
)
def correct_product_stock(
    product_id: int,
    stock_data: StockCorrection,
    db: Session = Depends(get_db)
):
    product = db.query(models.Product).filter(
        models.Product.id == product_id
    ).first()

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    product.stock_quantity = stock_data.actual_quantity

    db.commit()
    db.refresh(product)

    return product




@app.delete("/products/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = db.query(models.Product).filter(
        models.Product.id == product_id
    ).first()

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    db.delete(product)
    db.commit()

    return {
        "message": "Product deleted successfully"
    }

