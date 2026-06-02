import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.db.base import Base


class TradingSignal(Base):
    __tablename__ = "trading_signals"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    symbol: Mapped[str] = mapped_column(String, index=True)
    signal: Mapped[str] = mapped_column(String)
    confidence: Mapped[float] = mapped_column(Float)
    target_price: Mapped[float] = mapped_column(Float)
    prediction_source: Mapped[str] = mapped_column(String)
    outcome: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
