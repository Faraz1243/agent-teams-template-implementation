from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from .main import Base

class Sector(Base):
    __tablename__ = 'sectors'
    sector_key = Column(String(255), primary_key=True)
    sector_name = Column(String(255), unique=True, nullable=False)
    sector_description = Column(Text)
    
    # stocks = relationship("Stocks", back_populates="sector", cascade="all, delete-orphan")
    # sentiments = relationship("SectorSentiment", back_populates="sector")

