"""
Pydantic schemas for Polymarket API
"""

from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field


# Request parameter schemas
class PolymarketMarketsParams(BaseModel):
    """Parameters for GET /markets endpoint"""

    limit: int = 100
    offset: int | None = None
    order: str | None = None
    ascending: bool | None = None


class PolymarketEventsParams(BaseModel):
    """Parameters for GET /events/pagination endpoint"""

    limit: int = 100
    offset: int | None = None
    order: str | None = None
    ascending: bool | None = None


class PolymarketSeries(BaseModel):
    """Series associated with an event"""

    title: str | None = None
    subtitle: str | None = None
    description: str | None = None
    slug: str | None = None
    ticker: str | None = None
    series_type: str | None = Field(None, alias="seriesType")
    tags: list["PolymarketTag"] = Field(default_factory=list)
    categories: list["PolymarketCategory"] = Field(default_factory=list)


class PolymarketEvent(BaseModel):
    """Event from /events/pagination endpoint"""

    # Core identifiers
    id: str
    slug: str | None = None
    ticker: str | None = None

    # Event content
    title: str | None = None
    subtitle: str | None = None
    description: str | None = None
    category: str | None = None
    subcategory: str | None = None

    # Resolution
    resolution_source: str | None = Field(None, alias="resolutionSource")

    # Dates
    start_date: str | None = Field(None, alias="startDate")
    creation_date: str | None = Field(None, alias="creationDate")
    end_date: str | None = Field(None, alias="endDate")
    created_at: str | None = Field(None, alias="createdAt")
    updated_at: str | None = Field(None, alias="updatedAt")

    # Status flags
    active: bool | None = None
    closed: bool | None = None
    archived: bool | None = None
    new: bool | None = None
    featured: bool | None = None
    restricted: bool | None = None

    # Nested objects
    markets: list["PolymarketMarket"] = Field(default_factory=list)
    series: list[PolymarketSeries] = Field(default_factory=list)
    categories: list["PolymarketCategory"] = Field(default_factory=list)
    tags: list["PolymarketTag"] = Field(default_factory=list)

    model_config: ClassVar[ConfigDict] = ConfigDict(populate_by_name=True)


class PolymarketTag(BaseModel):
    """Tag/category for a market"""

    label: str | None = None
    slug: str | None = None


class PolymarketCategory(BaseModel):
    """Category for a market"""

    label: str | None = None
    slug: str | None = None


class PolymarketMarket(BaseModel):
    """Polymarket market (filtered to relevant fields only)"""

    # Core identifiers
    id: str
    slug: str | None = None
    question_id: str | None = Field(None, alias="questionID")

    # Market content
    question: str | None = None
    description: str | None = None
    outcomes: str | None = None  # JSON string of outcomes
    short_outcomes: str | None = Field(None, alias="shortOutcomes")
    category: str | None = None

    # Market metadata
    sponsor_name: str | None = Field(None, alias="sponsorName")
    market_type: str | None = Field(None, alias="marketType")
    sports_market_type: str | None = Field(None, alias="sportsMarketType")
    group_item_title: str | None = Field(None, alias="groupItemTitle")
    creator: str | None = None
    past_slugs: str | None = Field(None, alias="pastSlugs")

    # Dates (both string and datetime formats available)
    start_date: str | None = Field(None, alias="startDate")
    end_date: str | None = Field(None, alias="endDate")

    # Bounds
    lower_bound: str | None = Field(None, alias="lowerBound")
    upper_bound: str | None = Field(None, alias="upperBound")
    denomination_token: str | None = Field(None, alias="denominationToken")

    # Status flags
    active: bool | None = None
    closed: bool | None = None
    featured: bool | None = None

    # Nested objects
    events: list[PolymarketEvent] = Field(default_factory=list)
    categories: list[PolymarketCategory] = Field(default_factory=list)
    tags: list[PolymarketTag] = Field(default_factory=list)

    model_config: ClassVar[ConfigDict] = ConfigDict(populate_by_name=True)

    @property
    def event_titles(self) -> list[str]:
        """Extract event titles"""
        return [e.title for e in self.events if e.title]

    @property
    def tag_labels(self) -> list[str]:
        """Extract tag labels"""
        return [t.label for t in self.tags if t.label]

    @property
    def category_names(self) -> list[str]:
        """Extract category names"""
        return [c.label for c in self.categories if c.label]

    @property
    def event_descriptions(self) -> list[str]:
        """Extract event descriptions"""
        return [e.description for e in self.events if e.description]

    @property
    def all_text(self) -> str:
        """Concatenate all textual content for indexing"""
        parts = [
            self.question or "",
            self.description or "",
            self.outcomes or "",
            self.short_outcomes or "",
            self.category or "",
            self.sponsor_name or "",
            self.market_type or "",
            self.sports_market_type or "",
            self.group_item_title or "",
            " ".join(self.event_titles),
            " ".join(self.event_descriptions),
            " ".join(self.tag_labels),
            " ".join(self.category_names),
        ]
        return " ".join(p for p in parts if p).strip()
