import pandas as pd
import numpy as np
from typing import List
from backend.ingestion.schemas import NormalizedTick
from backend.schemas.features import FeatureVector

class FeatureEngine:
    """
    Computes technical and microstructure indicators from a buffer of market ticks.
    """
    @staticmethod
    def compute_features(ticks: List[NormalizedTick]) -> FeatureVector:
        if not ticks:
            raise ValueError("Empty tick buffer provided to FeatureEngine")
            
        df = pd.DataFrame([t.model_dump() for t in ticks])
        
        # Base columns
        df['close'] = df['last_price']
        
        # If volume is missing, fill with 1 to avoid div by zero
        if 'volume' not in df.columns or df['volume'].isnull().all():
            df['volume'] = 1.0
        df['volume'] = df['volume'].fillna(1.0)
        
        # We need high, low for ATR and VWAP. Calculate rolling high/low from ticks over a small window if missing.
        df['high'] = df['close'].rolling(window=10, min_periods=1).max()
        df['low'] = df['close'].rolling(window=10, min_periods=1).min()
        
        # Technical Indicators
        df['ema_9'] = df['close'].ewm(span=9, adjust=False).mean()
        df['ema_21'] = df['close'].ewm(span=21, adjust=False).mean()
        
        # RSI(14)
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14, min_periods=1).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=1).mean()
        rs = gain / loss.replace(0, np.nan)
        df['rsi_14'] = 100 - (100 / (1 + rs))
        df['rsi_14'] = df['rsi_14'].fillna(50)
        
        # MACD (12, 26, 9)
        ema_12 = df['close'].ewm(span=12, adjust=False).mean()
        ema_26 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = ema_12 - ema_26
        
        # ATR (14)
        prev_close = df['close'].shift(1).fillna(df['close'])
        tr1 = df['high'] - df['low']
        tr2 = (df['high'] - prev_close).abs()
        tr3 = (df['low'] - prev_close).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        df['atr'] = tr.rolling(window=14, min_periods=1).mean()
        
        # Bollinger Band Width (20, 2)
        sma_20 = df['close'].rolling(window=20, min_periods=1).mean()
        std_20 = df['close'].rolling(window=20, min_periods=1).std().fillna(0)
        upper_band = sma_20 + (std_20 * 2)
        lower_band = sma_20 - (std_20 * 2)
        df['bollinger_band_width'] = (upper_band - lower_band) / sma_20.replace(0, np.nan)
        df['bollinger_band_width'] = df['bollinger_band_width'].fillna(0)
        
        # ROC(5), ROC(15)
        df['roc_5'] = df['close'].pct_change(periods=5).fillna(0) * 100
        df['roc_15'] = df['close'].pct_change(periods=15).fillna(0) * 100
        
        # VWAP deviation
        df['typical_price'] = (df['high'] + df['low'] + df['close']) / 3
        df['cum_vp'] = (df['typical_price'] * df['volume']).cumsum()
        df['cum_v'] = df['volume'].cumsum()
        df['vwap'] = df['cum_vp'] / df['cum_v'].replace(0, np.nan)
        df['vwap_deviation'] = (df['close'] - df['vwap']) / df['vwap'].replace(0, np.nan)
        df['vwap_deviation'] = df['vwap_deviation'].fillna(0)
        
        # Market Microstructure (Since SmartAPI getLtpData doesn't provide these, we use 0 or neutral values)
        # In a real setup, we'd use websocket market depth
        df['buy_sell_ratio'] = 1.0
        df['order_book_imbalance'] = 0.0
        df['spread'] = df['close'] * 0.0005 # Simulated spread of 0.05%
        df['spread_mean'] = df['spread'].rolling(window=10, min_periods=1).mean()
        df['spread_std'] = df['spread'].rolling(window=10, min_periods=1).std().fillna(0)
        
        vol_sma_20 = df['volume'].rolling(window=20, min_periods=1).mean()
        df['volume_ratio'] = df['volume'] / vol_sma_20.replace(0, np.nan)
        df['volume_ratio'] = df['volume_ratio'].fillna(1.0)
        
        df['high_low_range'] = df['high'] - df['low']
        hl_range = df['high_low_range'].replace(0, np.nan)
        df['close_position'] = ((df['close'] - df['low']) / hl_range).fillna(0.5)
        
        # Final cleanup
        df = df.fillna(0)
        latest = df.iloc[-1]
        
        return FeatureVector(
            symbol=str(latest['symbol']),
            timestamp=latest['timestamp'].to_pydatetime() if hasattr(latest['timestamp'], 'to_pydatetime') else latest['timestamp'],
            rsi_14=float(latest['rsi_14']),
            macd=float(latest['macd']),
            atr=float(latest['atr']),
            bollinger_band_width=float(latest['bollinger_band_width']),
            ema_9=float(latest['ema_9']),
            ema_21=float(latest['ema_21']),
            roc_5=float(latest['roc_5']),
            roc_15=float(latest['roc_15']),
            vwap_deviation=float(latest['vwap_deviation']),
            buy_sell_ratio=float(latest['buy_sell_ratio']),
            order_book_imbalance=float(latest['order_book_imbalance']),
            spread_mean=float(latest['spread_mean']),
            spread_std=float(latest['spread_std']),
            volume_ratio=float(latest['volume_ratio']),
            high_low_range=float(latest['high_low_range']),
            close_position=float(latest['close_position'])
        )
