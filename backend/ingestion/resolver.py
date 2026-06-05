from typing import Optional

class SymbolResolver:
    """
    Resolves human-readable trading symbols to broker-specific symbol tokens.
    Currently uses a static mapping for V1 validation.
    Future: Dynamically load OpenAPIScripMaster.json.
    """
    
    # Static fallback map for NSE tokens
    _STATIC_MAP = {
        "NIFTY 50": "26000",
        "BANKNIFTY": "26009",
    }
    
    @classmethod
    def get_token(cls, symbol: str) -> Optional[str]:
        """
        Get the Angel One symbol token for a given symbol.
        """
        return cls._STATIC_MAP.get(symbol.upper())

    @classmethod
    def get_exchange(cls, symbol: str) -> str:
        """
        Get the exchange for a given symbol.
        Default to NSE for indices.
        """
        # In the future, this can be derived from the scrip master
        return "NSE"
