from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base, BaseModel
from datetime import datetime
from typing import Optional

# Add enums for better type safety
class SentimentScore(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

class TrafficSource(str, Enum):
    DIRECT = "direct"
    ORGANIC = "organic"
    PAID = "paid"
    SOCIAL = "social"
    REFERRAL = "referral"

class TrafficSnapshot(BaseModel):
    __tablename__ = "traffic_snapshots"
    
    brand_id = Column(Integer, ForeignKey("brands.id"))
    visits = Column(Integer)
    page_views = Column(Integer)
    bounce_rate = Column(Float)
    avg_visit_duration = Column(Float)
    date = Column(DateTime)
    
    # Traffic sources
    direct_traffic = Column(Integer)
    organic_traffic = Column(Integer)
    paid_traffic = Column(Integer)
    social_traffic = Column(Integer)
    referral_traffic = Column(Integer)
    
    # Geographic data
    country_distribution = Column(JSON)
    device_distribution = Column(JSON)
    
    brand = relationship("Brand", back_populates="traffic_snapshots")

class SEOInfo(BaseModel):
    __tablename__ = "seo_info"
    
    brand_id = Column(Integer, ForeignKey("brands.id"))
    keywords = Column(Integer)
    organic_traffic = Column(Integer)
    paid_traffic = Column(Integer)
    organic_keywords = Column(Integer)
    paid_keywords = Column(Integer)
    seo_score = Column(Float)
    date = Column(DateTime)
    
    brand = relationship("Brand", back_populates="seo_info")

class SentimentResult(BaseModel):
    __tablename__ = "sentiment_results"
    
    post_id = Column(Integer, ForeignKey("social_posts.id"))
    review_id = Column(Integer, ForeignKey("reviews.id"), nullable=True)
    score = Column(Float)
    label = Column(Enum(SentimentScore))
    confidence = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    post = relationship("SocialPost", back_populates="sentiment")
    review = relationship("Review", back_populates="sentiment")

class SocialPost(BaseModel):
    __tablename__ = "social_posts"
    
    brand_id = Column(Integer, ForeignKey("brands.id"))
    source = Column(String(50))  # instagram, facebook, etc.
    content = Column(Text)
    engagement = Column(JSON)  # likes, comments, shares
    media_url = Column(String(500))
    sentiment_score = Column(Float, nullable=True)
    sentiment_label = Column(Enum(SentimentScore), nullable=True)
    timestamp = Column(DateTime)
    
    sentiment = relationship("SentimentResult", uselist=False, back_populates="post")
    brand = relationship("Brand", back_populates="social_posts")

class Review(BaseModel):
    __tablename__ = "reviews"
    
    brand_id = Column(Integer, ForeignKey("brands.id"))
    source = Column(String(50))  # instagram, facebook, etc.
    content = Column(Text)
    rating = Column(Float)
    sentiment_score = Column(Float, nullable=True)
    sentiment_label = Column(Enum(SentimentScore), nullable=True)
    timestamp = Column(DateTime)
    
    sentiment = relationship("SentimentResult", uselist=False, back_populates="review")
    brand = relationship("Brand", back_populates="reviews")

# Update Brand model to include relationships
class Brand(BaseModel):
    __tablename__ = "brands"
    
    name = Column(String(255), unique=True, index=True)
    description = Column(Text, nullable=True)
    website = Column(String(255), nullable=True)
    logo_url = Column(String(255), nullable=True)
    social_handles = Column(JSON)  # {instagram: "handle", facebook: "handle", etc.}
    
    traffic_snapshots = relationship("TrafficSnapshot", back_populates="brand")
    seo_info = relationship("SEOInfo", back_populates="brand")
    social_posts = relationship("SocialPost", back_populates="brand")
    reviews = relationship("Review", back_populates="brand")
    
    # Add indexes for faster queries
    __table_args__ = (
        Index('ix_brand_website', 'website'),
        Index('ix_brand_social_handles', 'social_handles'),
    )
