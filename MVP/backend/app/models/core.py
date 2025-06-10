from sqlalchemy import Column, String, Integer, Float, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from .base import Base, BaseModel

class Brand(BaseModel):
    __tablename__ = "brands"
    
    name = Column(String(255), unique=True, index=True)
    description = Column(Text, nullable=True)
    website = Column(String(255), nullable=True)
    logo_url = Column(String(255), nullable=True)
    social_links = Column(JSON, nullable=True)
    products = relationship("Product", back_populates="brand")

class Product(BaseModel):
    __tablename__ = "products"
    
    name = Column(String(255), index=True)
    description = Column(Text, nullable=True)
    brand_id = Column(Integer, ForeignKey("brands.id"))
    sku = Column(String(50), unique=True, index=True)
    category = Column(String(100))
    brand = relationship("Brand", back_populates="products")
    prices = relationship("PriceSnapshot", back_populates="product")
    reviews = relationship("Review", back_populates="product")

class PriceSnapshot(BaseModel):
    __tablename__ = "price_snapshots"
    
    product_id = Column(Integer, ForeignKey("products.id"))
    price = Column(Float)
    currency = Column(String(3))
    source = Column(String(50))
    product = relationship("Product", back_populates="prices")

class Review(BaseModel):
    __tablename__ = "reviews"
    
    product_id = Column(Integer, ForeignKey("products.id"))
    rating = Column(Float)
    content = Column(Text)
    source = Column(String(50))
    sentiment_score = Column(Float)
    product = relationship("Product", back_populates="reviews")

class SocialPost(BaseModel):
    __tablename__ = "social_posts"
    
    content = Column(Text)
    source = Column(String(50))  # e.g., facebook, instagram
    engagement = Column(JSON)  # likes, shares, comments
    sentiment_score = Column(Float)
    brand_id = Column(Integer, ForeignKey("brands.id"))
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)

class JobPosting(BaseModel):
    __tablename__ = "job_postings"
    
    title = Column(String(255))
    company = Column(String(255))
    location = Column(String(255))
    description = Column(Text)
    salary = Column(String(100))  # e.g., "5000-10000 USD"
    source = Column(String(50))  # e.g., adzuna
    brand_id = Column(Integer, ForeignKey("brands.id"))
