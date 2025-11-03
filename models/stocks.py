from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date, JSON, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy import func
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base
from sqlalchemy import UniqueConstraint, Index
from typing import Optional

# Base = declarative_base()
from .main import Base


class Stocks(Base):
    __tablename__ = 'stocks'
    ticker = Column(String(10), primary_key=True, nullable=False)
    company_name = Column(String(255), nullable=False)
    address1 = Column(String(255))
    address2 = Column(String(255))
    city = Column(String(100))
    zip = Column(String(20))
    country = Column(String(100))
    phone = Column(String(50))
    fax = Column(String(50))
    website = Column(String(255))
    industry = Column(String(255))
    created_at = Column(TIMESTAMP, default=func.now())
    updated_at = Column(TIMESTAMP, default=func.now(), onupdate=func.now())
    sector_key = Column(String(255), ForeignKey('sectors.sector_key'), nullable=True)
    
    # sector = relationship("Sector", back_populates="stocks")
    daily_data = relationship("DailyData", back_populates="stock", cascade="all, delete-orphan")
    # sentiments = relationship("StockSentiment", back_populates="stock")
    # dividends = relationship("Dividend", back_populates="stock", cascade="all, delete-orphan")
    # news = relationship("CompanyNews", back_populates="stock", cascade="all, delete-orphan")



class DailyData(Base):
    __tablename__ = 'daily_data'
    daily_data_id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(10), ForeignKey('stocks.ticker'), nullable=False)
    date = Column(Date, nullable=False)
    open = Column(Numeric(10, 2))
    high = Column(Numeric(10, 2))
    low = Column(Numeric(10, 2))
    close = Column(Numeric(10, 2))
    volume = Column(Integer)
    technical_indicators = Column(JSONB)
    created_at = Column(TIMESTAMP, default=func.now())
    updated_at = Column(TIMESTAMP, default=func.now(), onupdate=func.now())
    
    stock = relationship("Stocks", back_populates="daily_data")
    
    __table_args__ = (
        UniqueConstraint('ticker', 'date'),
        Index('idx_daily_data_date', 'date'),
        Index('idx_daily_data_ticker_date', 'ticker', 'date'),
        Index('idx_daily_data_updated', 'updated_at')
    )

    @property
    def median(self) -> Optional[float]:
        """Calculate median as (high + low) / 2"""
        if self.high is not None and self.low is not None:
            return float((self.high + self.low) / 2)
        return None
