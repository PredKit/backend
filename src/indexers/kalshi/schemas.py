"""
Pydantic schemas for Kalshi API
"""

from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field


# Request parameter schemas
class KalshiMarketsParams(BaseModel):
    """Parameters for GET /markets endpoint"""

    limit: int = 100
    cursor: str | None = None


class KalshiEventsParams(BaseModel):
    """Parameters for GET /events endpoint"""

    limit: int = 100
    cursor: str | None = None
    with_nested_markets: bool = False


class KalshiSeriesParams(BaseModel):
    """Parameters for GET /series endpoint"""

    limit: int = 100
    cursor: str | None = None


class KalshiMarket(BaseModel):
    """Kalshi market (filtered to relevant fields only)"""

    # Core identifiers
    ticker: str
    event_ticker: str | None = Field(None, alias="event_ticker")
    market_type: str | None = Field(None, alias="market_type")

    # Market content
    title: str | None = None
    subtitle: str | None = None
    yes_sub_title: str | None = Field(None, alias="yes_sub_title")
    no_sub_title: str | None = Field(None, alias="no_sub_title")

    # Rules
    rules_primary: str | None = Field(None, alias="rules_primary")
    rules_secondary: str | None = Field(None, alias="rules_secondary")

    # Metadata
    category: str | None = None
    status: str | None = None

    # Times
    open_time: str | None = Field(None, alias="open_time")
    close_time: str | None = Field(None, alias="close_time")
    expiration_time: str | None = Field(None, alias="expiration_time")

    # Result
    result: str | None = None

    model_config: ClassVar[ConfigDict] = ConfigDict(populate_by_name=True)

    @property
    def all_text(self) -> str:
        """Concatenate all textual content for indexing"""
        parts = [
            self.title or "",
            self.subtitle or "",
            self.yes_sub_title or "",
            self.no_sub_title or "",
            self.rules_primary or "",
            self.rules_secondary or "",
            self.category or "",
        ]
        return " ".join(p for p in parts if p).strip()


class KalshiEvent(BaseModel):
    """Kalshi event"""

    event_ticker: str | None = Field(None, alias="event_ticker")
    title: str | None = None
    sub_title: str | None = Field(None, alias="sub_title")
    category: str | None = None
    series_ticker: str | None = Field(None, alias="series_ticker")
    markets: list[KalshiMarket] = Field(default_factory=list)

    model_config: ClassVar[ConfigDict] = ConfigDict(populate_by_name=True)


class KalshiSeries(BaseModel):
    """Kalshi series"""

    ticker: str
    title: str | None = None
    category: str | None = None
    frequency: str | None = None
    tags: list[str] | None = None

    model_config: ClassVar[ConfigDict] = ConfigDict(populate_by_name=True)
