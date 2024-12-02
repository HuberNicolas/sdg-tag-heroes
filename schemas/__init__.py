from .publications.author import AuthorSchemaBase, AuthorSchemaFull

from .publications.publication import PublicationSchemaBase, PublicationSchemaFull

from .sdg.target import SDGTargetSchemaBase, SDGTargetSchemaFull
from .sdg.goal import SDGGoalSchemaBase, SDGGoalSchemaFull

from .dimensionality_reduction import DimensionalityReductionSchemaBase, DimensionalityReductionSchemaFull

from .sdg_prediction import SDGPredictionSchemaBase, SDGPredictionSchemaFull

from .sdg_label_summary import SDGLabelSummarySchemaBase, SDGLabelSummarySchemaFull
from .sdg_label_history import SDGLabelHistorySchemaBase, SDGLabelHistorySchemaFull
from .sdg_label_decision import SDGLabelDecisionSchemaBase, SDGLabelDecisionSchemaFull


from .users.user import UserSchemaFull

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

    "SDGPredictionSchemaBase",
    "SDGPredictionSchemaFull",


    "SDGLabelSummarySchemaBase",
    "SDGLabelSummarySchemaFull",

    "SDGLabelHistorySchemaFull",
    "SDGLabelHistorySchemaFull",

    "SDGLabelDecisionSchemaBase",
    "SDGLabelDecisionSchemaFull",

    "UserSchemaFull",
]
