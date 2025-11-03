from sqlalchemy import Column, String, ForeignKey, Date, JSON, Numeric, Enum
from .metrics import PeriodEnum
from .main import Base

class FinancialsView(Base):
    __tablename__ = "financials_view"
    __table_args__ = {"autoload_with": None}  # if you want reflection

    ticker = Column(String(20), primary_key=True)
    statement_type = Column(String(100), primary_key=True)
    period_end = Column(Date, primary_key=True) 
    period_type = Column(
        Enum(PeriodEnum, name="period_enum", create_type=False)  # 👈 force it to use existing DB type
    )
    financials = Column(JSON)   # jsonb_object_agg → JSON

    def __repr__(self):
        return (
            f"<FinancialsView(ticker={self.ticker}, "
            f"statement_type={self.statement_type}, "
            f"period_end={self.period_end}, "
            f"period_type={self.period_type}, "
            f"financials={self.financials})>"
        )