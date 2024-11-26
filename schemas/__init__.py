from .publications.author import AuthorSchemaBase, AuthorSchemaFull

from .publications.publication import PublicationSchemaBase, PublicationSchemaFull

from .sdg.target import SDGTargetSchemaBase, SDGTargetSchemaFull
from .sdg.goal import SDGGoalSchemaBase, SDGGoalSchemaFull

from .dimensionality_reduction import DimensionalityReductionSchemaBase, DimensionalityReductionSchemaFull


# Export all models for external use
__all__ = [
    "AuthorSchemaBase",
    "AuthorSchemaFull",


    "PublicationSchemaBase",
    "PublicationSchemaFull",

    "SDGTargetSchemaBase",
    "SDGTargetSchemaFull",

    "SDGGoalSchemaBase",
    "SDGGoalSchemaFull",

    "DimensionalityReductionSchemaBase",
    "DimensionalityReductionSchemaFull",
]
