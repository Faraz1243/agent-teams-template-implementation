from sqlalchemy import (
    Column, String, Integer, Text, Date, Numeric, ForeignKey, 
    UniqueConstraint, DateTime, func
)
from sqlalchemy.orm import relationship
from .main import Base

class Dividend(Base):
    __tablename__ = "dividends"
    
    id = Column(Integer, primary_key=True)
    ticker = Column(String(10), ForeignKey("stocks.ticker", ondelete="CASCADE"), nullable=False)
    company_name = Column(Text, nullable=False)
    announcement_date = Column(Date, nullable=False)
    eligibility_date = Column(Date, nullable=False)
    distribution_method = Column(String(50))
    distribution_date = Column(Date)
    dividend_amount = Column(Numeric(10, 3))
    
    # created_at = Column(DateTime, server_default=func.now())
    # updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # __table_args__ = (
    #     UniqueConstraint('ticker', 'announcement_date', 'eligibility_date', name='unique_dividend_entry'),
    # )

    # # Optional: relationship to Stock model if you want to access stock data
    # stock = relationship("Stocks", back_populates="dividends")
