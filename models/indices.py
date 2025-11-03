from sqlalchemy import (
    Column, String, Numeric, Date, ForeignKey, Index
)
from .main import Base

class StockIndex(Base):  
    __tablename__ = "stock_indices"
    symbol = Column(String(50), primary_key=True)
    ticker = Column(String(50))
    name = Column(String(100))
    country = Column(String(50))
    group = Column(String(50))
    unit = Column(String(20))
    frequency = Column(String(20))

class IndexDailyData(Base):
    __tablename__ = "global_indices_daily_data"
    symbol = Column(String(50), ForeignKey("stock_indices.symbol"), primary_key=True)  # Updated foreign key
    date = Column(Date, primary_key=True)
    open = Column(Numeric(10, 2))
    high = Column(Numeric(10, 2))
    low = Column(Numeric(10, 2))
    close = Column(Numeric(10, 2))
    
    __table_args__ = (
        Index('idx_index_daily_data_symbol_date', 'symbol', 'date'),  # Composite index
        Index('idx_index_daily_data_date', 'date'),  # Index for date-based queries
    )