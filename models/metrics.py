import enum, math

from sqlalchemy import (
    Column, Null, String, Numeric, Date, Boolean, Text, ForeignKey, TIMESTAMP, Enum, ARRAY, DECIMAL
)
from sqlalchemy.sql import func
from .main import Base


# Step 1: Enum for periods
class PeriodEnum(enum.Enum):
    FY = "FY"
    Q = "Q"
    LTM = "LTM"
    YTD = "YTD"
    D = "D"
    Y = "Y"  
    FY_PLUS_1 = "FY+1"
 
class Metrics(Base):
    __tablename__ = "metrics"

    slug = Column(String(100), primary_key=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100))
    statement_type = Column(String(100))  # e.g. "Computed", "Balance Sheet"
    
    available_periods = Column(
        ARRAY(Enum(PeriodEnum, name="period_enum")),  # 👈 fixed
        nullable=True
    )  # e.g. ["Q", "FY", "D"]

    default_period = Column(
        Enum(PeriodEnum, name="period_enum"),  # 👈 fixed
        nullable=True
    )

    premium = Column(Boolean, default=False)
    description = Column(Text)


    @staticmethod
    def getEnums(text: str):
        if not text or (isinstance(text, float) and math.isnan(text)):
            return None  # no periods available

        enums = []
        for part in text.replace(" ", "").split(','):
            try:
                enums.append(PeriodEnum[part])  # only valid enum members
            except KeyError:
                continue  # skip invalid entries
        if len(enums)==0:
            return None
        return enums

    @staticmethod
    def getSingleEnum(text:str):
        enum = None
        try:
            enum = PeriodEnum[text]
        except KeyError:
            pass  # skip invalid entries
        return enum
        

# Step 3: Metric values table
class MetricValues(Base):
    __tablename__ = "metric_values"

    slug = Column(String(100), ForeignKey("metrics.slug"), primary_key=True)
    ticker = Column(String(20), primary_key=True)
    period_type = Column(Enum(PeriodEnum, name="period_enum", create_type=False),nullable=False)
    period_start = Column(Date, primary_key=True)
    period_end = Column(Date, primary_key=True)
    value = Column(Numeric(20, 6), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
