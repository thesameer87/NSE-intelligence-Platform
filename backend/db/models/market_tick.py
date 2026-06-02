import uuid
from datetime import date, datetime

from sqlalchemy import BigInteger, Boolean, Date, DateTime, Float, String
from typing import Optional
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.db.base import Base


class IntradayTick(Base):
    __tablename__ = "intraday_ticks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    symbol: Mapped[str] = mapped_column(String, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    ltp: Mapped[float] = mapped_column(Float)
    bid_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ask_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    bid_qty: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ask_qty: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    volume: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    cold_storage_uploaded: Mapped[bool] = mapped_column(Boolean, default=False)


class DailyOHLCV(Base):
    __tablename__ = "daily_ohlcv"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    symbol: Mapped[str] = mapped_column(String, index=True)
    trade_date: Mapped[date] = mapped_column(Date, index=True)
    open: Mapped[float] = mapped_column(Float)
    high: Mapped[float] = mapped_column(Float)
    low: Mapped[float] = mapped_column(Float)
    close: Mapped[float] = mapped_column(Float)
    volume: Mapped[int] = mapped_column(BigInteger)
