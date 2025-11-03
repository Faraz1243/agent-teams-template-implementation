from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Integer
from sqlalchemy import (Integer,Text,DateTime,Numeric,Date,func,UniqueConstraint,ForeignKey, Enum,ARRAY,JSON)
from sqlalchemy import Float, Boolean, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB

from sqlalchemy.schema import PrimaryKeyConstraint
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY

from .main import Base

import pytz
SAUDI_TZ = pytz.timezone("Asia/Riyadh")
def saudi_now():
    return datetime.now(SAUDI_TZ).replace(tzinfo=None)

class NerSentimentCache(Base):
    __tablename__ = "ner_sentiment_cache"
    __table_args__ = (PrimaryKeyConstraint("url", "llm_model"),)

    url = Column(Text, nullable=False)
    llm_model = Column(Text, nullable=False)  

    source_table = Column(Text)  
    date = Column(TIMESTAMP)
    language = Column(String(10))   

    relevance = Column(Text)
    analysis = Column(JSONB)
    distributed = Column(Boolean, default=False)


class SentimentAggregate(Base):
    __tablename__ = "sentiment_aggregate_view"

    entity_id = Column(String, primary_key=True)
    llm_model = Column(String)
    entity_type = Column(String)
    aggregation_time = Column(DateTime, primary_key=True)
    short_term_sentiment_avg = Column(Float)
    long_term_sentiment_avg = Column(Float)
    weighted_importance_avg = Column(Float)
    total_mentions = Column(Integer)

class DailySentimentBase(Base):
    __abstract__ = True

    @declared_attr
    def date(cls):
        return Column(Date, nullable=False)

    sentiment_id = Column(Integer, primary_key=True, autoincrement=True)
    short_term_sentiment = Column(Numeric(4, 2), nullable=False)
    long_term_sentiment = Column(Numeric(4, 2), nullable=False)
    sentiment_type = Column(String(20), nullable=False)
    total_importance = Column(Float, nullable=False)
    llm_model = Column(Text, nullable=False, default="openai/gpt-oss-120b")
    frequency = Column(
        Enum("D", "W", "M", "Q", "Y", name="frequency_enum"),
        nullable=False,
        default="D"
    )

    
    created_at = Column(DateTime, default=saudi_now)
    updated_at = Column(DateTime, default=saudi_now, onupdate=saudi_now)

class StockSentiment(DailySentimentBase):
    __tablename__ = 'stock_sentiments'
    __table_args__ = (UniqueConstraint('date', 'ticker', 'sentiment_type', 'llm_model', 'frequency', name='uq_date_ticker_type_model_freq'),)

    ticker = Column(String(10), ForeignKey('stocks.ticker', ondelete='CASCADE'), nullable=False)    
    # stock = relationship("Stocks", back_populates="sentiments")


class SectorSentiment(DailySentimentBase):
    __tablename__ = 'sector_sentiments'
    __table_args__ = (UniqueConstraint('date', 'sector_key', 'sentiment_type', 'llm_model', 'frequency', name='uq_date_sector_key_type_model_freq'),)

    notes = Column(Text, nullable=True)
    sector_key = Column(String(255), ForeignKey('sectors.sector_key', ondelete='CASCADE'), nullable=False)
    # sector = relationship("Sector", back_populates="sentiments")


class MarketSentiment(DailySentimentBase):
    __tablename__ = 'market_sentiments'
    __table_args__ = (UniqueConstraint('date', 'sentiment_type', 'llm_model', 'frequency', name='uq_date_type_model_freq'),)

    notes = Column(Text, nullable=True)


class Sentiment(Base):
    __abstract__ = True  # Makes SQLAlchemy ignore this as a table

    sentiment_id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(Text, nullable=False)
    source_table = Column(Text, nullable=False)
    date = Column(Date, nullable=False)
    short_term_sentiment = Column(Float)
    long_term_sentiment = Column(Float)
    importance = Column(Float)
    llm_notes = Column(JSONB, nullable=False, default={"english_note": "", "arabic_note": ""})
    language = Column(Text)
    relevance = Column(Text)
    llm_model = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())

    news_categories = Column(ARRAY(Text), default=[])
    short_term_impact_horizon = Column(Integer, default=0, nullable=False)
    long_term_impact_horizon = Column(Integer, default=0, nullable=False)
    confidence = Column(Float, default=0, nullable=False)
    event_type = Column(Text, default="", nullable=False)
    shock_level = Column(Text, default="", nullable=False)

class SentimentRaw(Sentiment):
    __abstract__ = True  # Makes SQLAlchemy ignore this as a table

    uniqueness_check = Column(Boolean, default=False)

class StockSentimentRaw(SentimentRaw):
    __tablename__ = 'stock_sentiments_raw'

    ticker = Column(Text, ForeignKey('stocks.ticker', ondelete='CASCADE'), nullable=False)

    __table_args__ = (
        UniqueConstraint('url', 'ticker', 'llm_model', name='unique_article_ticker_llm'),
    )


class SectorSentimentRaw(SentimentRaw):
    __tablename__ = 'sector_sentiments_raw'

    sector_key = Column(Text, ForeignKey('sectors.sector_key', ondelete='CASCADE'), nullable=False)

    __table_args__ = (
        UniqueConstraint('url', 'sector_key', 'llm_model', name='unique_article_sector_llm'),
    )


class MarketSentimentRaw(SentimentRaw):
    __tablename__ = 'market_sentiments_raw'

    __table_args__ = (
        UniqueConstraint('url', 'llm_model', name='unique_article_llm'),
    )


class StockSentimentClean(Sentiment):
    __tablename__ = 'stock_sentiments_clean'

    ticker = Column(Text, ForeignKey('stocks.ticker', ondelete='CASCADE'), nullable=False)

    __table_args__ = (
        UniqueConstraint('url', 'ticker', 'llm_model', name='unique_article_ticker_llm_clean'),
    )


class SectorSentimentClean(Sentiment):
    __tablename__ = 'sector_sentiments_clean'

    sector_key = Column(Text, ForeignKey('sectors.sector_key', ondelete='CASCADE'), nullable=False)

    __table_args__ = (
        UniqueConstraint('url', 'sector_key', 'llm_model', name='unique_article_sector_llm_clean'),
    )


class MarketSentimentClean(Sentiment):
    __tablename__ = 'market_sentiments_clean'

    __table_args__ = (
        UniqueConstraint('url', 'llm_model', name='unique_article_llm_clean'),
    )

class Card(Base):
    __tablename__ = "cards"

    entity_id = Column(String, nullable=False, primary_key=True)
    date = Column(Date, nullable=False, primary_key=True)

    short_term_sentiment = Column(Float, nullable=False)
    long_term_sentiment = Column(Float, nullable=False)
    importance = Column(Float, nullable=False)

    short_term_impact_horizon = Column(Integer, nullable=False, default=0)
    long_term_impact_horizon = Column(Integer, nullable=False, default=0)
    confidence = Column(Float, nullable=False, default=0.0)

    llm_notes = Column(
        JSON,
        nullable=False,
        default=lambda: {"english_note": "", "arabic_note": ""}
    )
    llm_model = Column(Text, nullable=False)

    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Card(entity_id={self.entity_id}, date={self.date}, STS={self.short_term_sentiment}, LTS={self.long_term_sentiment})>"