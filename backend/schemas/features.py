from datetime import datetime
from backend.schemas.common import BaseSchema
from pydantic import Field

class FeatureVector(BaseSchema):
    """
    Strictly typed feature vector for ML inference.
    Contains exactly the fields expected by the LightGBM models.
    """
    symbol: str
    timestamp: datetime
    
    # Technical Indicators
    rsi_14: float = Field(..., description="14-period Relative Strength Index")
    macd: float = Field(..., description="Moving Average Convergence Divergence")
    atr: float = Field(..., description="Average True Range")
    bollinger_band_width: float = Field(..., description="Width of Bollinger Bands")
    ema_9: float = Field(..., description="9-period Exponential Moving Average")
    ema_21: float = Field(..., description="21-period Exponential Moving Average")
    roc_5: float = Field(..., description="5-period Rate of Change")
    roc_15: float = Field(..., description="15-period Rate of Change")
    vwap_deviation: float = Field(..., description="Deviation from Volume Weighted Average Price")
    
    # Market Microstructure
    buy_sell_ratio: float = Field(..., description="Ratio of Buy to Sell volumes")
    order_book_imbalance: float = Field(..., description="Order Book Imbalance (OBI)")
    spread_mean: float = Field(..., description="Mean of bid-ask spread")
    spread_std: float = Field(..., description="Standard deviation of bid-ask spread")
    volume_ratio: float = Field(..., description="Volume ratio against historical average")
    high_low_range: float = Field(..., description="Range between high and low price")
    close_position: float = Field(..., description="Position of close price relative to high-low range")
