from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class QueryPlan(BaseModel):
    select: list[str] = Field(default_factory=lambda: ["*"])
    table: str = "facility"
    joins: list[str] = Field(default_factory=list)
    where: list[str] = Field(default_factory=list)
    group_by: list[str] = Field(default_factory=list)
    order_by: list[str] = Field(default_factory=list)
    limit: Optional[int] = None


class QueryIntent(BaseModel):
    metric: Optional[str] = None
    location: Optional[str] = None
    facility_type: Optional[str] = None
    location_type: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    sub_district: Optional[str] = None
