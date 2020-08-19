from enum import Enum
from datetime import date
from datetime import timedelta
from pydantic import BaseModel
from pydantic import Field


class AggregationPeriod(str, Enum):
    by_year = "by_year"
    by_month = "by_month"
    by_day = "by_day"


class LikesAggregationPayload(BaseModel):
    agg_period: AggregationPeriod = AggregationPeriod.by_day
    date_from: date = Field(default_factory=lambda: date.today() - timedelta(weeks=4))
    date_to: date = Field(default_factory=date.today)
    
