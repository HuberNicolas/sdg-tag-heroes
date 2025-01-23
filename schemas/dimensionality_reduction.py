from datetime import datetime
from typing import Optional, Dict, List

from pydantic import BaseModel


class DimensionalityReductionSchemaBase(BaseModel):
    dim_red_id: int
    publication_id: int
    reduction_technique: Optional[str]
    reduction_shorthand: Optional[str]
    sdg: int
    level: int
    x_coord: float
    y_coord: float
    z_coord: Optional[float]
    reduction_details: Optional[str]

    model_config = {
        "from_attributes": True  # Enables ORM-style model validation
    }


class DimensionalityReductionSchemaFull(DimensionalityReductionSchemaBase):
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True  # Enables ORM-style model validation
    }


# Not directly derived from models
# Todo: Generate TS type
class UserCoordinatesSchema(BaseModel):
    x_coord: float
    y_coord: float
    z_coord: Optional[float] = 0.0  # Default z-coordinate is 0.0 if not provided
    embedding_time: float
    model_loading_time: float
    umap_reduction_transform_time: float

    class Config:
        json_schema_extra = {
            "example": {
                "x": 0.1234,
                "y": -0.5678,
                "z": 0.0,
                "embedding_time": 0.045,
                "model_loading_time": 0.012,
                "umap_reduction_transform_time": 0.009
            }
        }



### One Endpoint
class FilteredSDGStatisticsSchema(BaseModel):
    limit: int
    retrieved_count: int
    min_prediction_value: Optional[float]
    max_prediction_value: Optional[float]
    publications_per_model: Dict[str, int]

class FilteredDimensionalityReductionStatisticsSchema(BaseModel):
    statistics: Dict[str, FilteredSDGStatisticsSchema]  # Includes general and SDG-specific statistics, any is actual SDGStatisticsSchema
    dimensionality_reductions: Dict[str, List[DimensionalityReductionSchemaFull]]

    class Config:
        json_schema_extra = {
            "example": {
                "statistics": {
                    "general_range": {"min_value": 0.98, "max_value": 0.99},
                    "sdg_statistics": {
                        "sdg1": {
                            "limit": 10,
                            "retrieved_count": 5,
                            "min_prediction_value": 0.981,
                            "max_prediction_value": 0.989,
                            "publications_per_model": {"Aurora": 5}
                        }
                    }
                },
                "dimensionality_reductions": {
                    "sdg1": [
                        {
                            "dim_red_id": 101,
                            "publication_id": 202,
                            "reduction_technique": "t-SNE",
                            "reduction_shorthand": "t-SNE-30-0.5-3",
                            "sdg": 1,
                            "level": 2,
                            "x_coord": 0.456,
                            "y_coord": -0.123,
                            "z_coord": 0.789,
                            "created_at": "2025-01-02T12:00:00",
                            "updated_at": "2025-01-02T13:00:00"
                        }
                    ]
                }
            }
        }




### One Endpoint
class GroupedSDGStatisticsSchema(BaseModel):
    total_levels: int
    total_reductions: int


class GroupedDimensionalityReductionStatisticsSchema(BaseModel):
    total_sdg_groups: int
    total_levels: int
    total_dimensionality_reductions: int
    sdg_breakdown: Dict[str, GroupedSDGStatisticsSchema]

class GroupedDimensionalityReductionResponseSchema(BaseModel):
    dimensionality_reductions: Dict[str, Dict[str, List[DimensionalityReductionSchemaFull]]]
    stats: GroupedDimensionalityReductionStatisticsSchema

    class Config:
        json_schema_extra = {
            "example": {
                "dimensionality_reductions": {
                    "sdg1": {
                        "level1": [
                            {
                                "dim_red_id": 123,
                                "publication_id": 456,
                                "reduction_technique": "UMAP",
                                "reduction_shorthand": "UMAP-15-0.1-2",
                                "x_coord": 0.123,
                                "y_coord": -0.456,
                                "z_coord": 0.789,
                                "sdg": 1,
                                "level": 1,
                                "created_at": "2025-01-01T12:34:56",
                                "updated_at": "2025-01-01T12:34:56"
                            }
                        ]
                    }
                },
                "stats": {
                    "total_sdg_groups": 1,
                    "total_levels": 1,
                    "total_dimensionality_reductions": 1,
                    "sdg_breakdown": {
                        "sdg1": {
                            "total_levels": 1,
                            "total_reductions": 1
                        }
                    }
                }
            }
        }
