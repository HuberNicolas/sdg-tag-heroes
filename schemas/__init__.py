# Note: This was/should be deactivated as the circular imports are hard to handle for automatic schema generation via pydantic-to-typescript
print("Initializing schemas")
from .authentication import UserDataSchemaBase, UserDataSchemaFull, TokenDataSchemaBase, TokenDataSchemaFull, LoginSchemaBase, LoginSchemaFull

from .sdgs.goal import SDGGoalSchemaBase, SDGGoalSchemaFull
from .sdgs.target import SDGTargetSchemaBase, SDGTargetSchemaFull

from .users.user import UserSchemaBase, UserSchemaFull
from .users.admin import AdminSchemaBase, AdminSchemaFull
from .users.expert import ExpertSchemaBase, ExpertSchemaFull
from .users.labeler import LabelerSchemaBase, LabelerSchemaFull
from .users.group import GroupSchemaBase, GroupSchemaFull

from .author import AuthorSchemaBase, AuthorSchemaFull
from .publication import PublicationSchemaBase, PublicationSchemaFull

from .faculty import FacultySchemaBase, FacultySchemaFull
from .institute import InstituteSchemaBase, InstituteSchemaFull
from .division import DivisionSchemaBase, DivisionSchemaFull

from .dimensionality_reduction import DimensionalityReductionSchemaBase, DimensionalityReductionSchemaFull

from .sdg_prediction import SDGPredictionSchemaBase, SDGPredictionSchemaFull
from .sdg_target_prediction import SDGTargetPredictionSchemaBase, SDGTargetPredictionSchemaFull
from .sdg_label_summary import SDGLabelSummarySchemaBase, SDGLabelSummarySchemaFull
from .sdg_label_history import SDGLabelHistorySchemaBase, SDGLabelHistorySchemaFull
from .sdg_label_decision import SDGLabelDecisionSchemaBase, SDGLabelDecisionSchemaFull
from .sdg_user_label import SDGUserLabelSchemaBase, SDGUserLabelSchemaFull
from .sdg_user_label import SDGLabelDistribution, UserVotingDetails, SDGUserLabelStatisticsSchema # NON-Entity-derived

from .vote import VoteSchemaBase, VoteSchemaFull
from .annotation import AnnotationSchemaBase, AnnotationSchemaFull

from .sdg_coin_wallet_history import SDGCoinWalletHistorySchemaBase, SDGCoinWalletHistorySchemaFull
from .sdg_coin_wallet import SDGCoinWalletSchemaBase, SDGCoinWalletSchemaFull
from .sdg_xp_bank_history import SDGXPBankHistorySchemaBase, SDGXPBankHistorySchemaFull
from .sdg_xp_bank import SDGXPBankSchemaBase, SDGXPBankSchemaFull

from .fact import FactSchemaBase, FactSchemaFull
from .summary import SummarySchemaBase, SummarySchemaFull

from .achievement import AchievementSchemaBase, AchievementSchemaFull
from .inventory import InventorySchemaBase, InventorySchemaFull
from .inventory_achievement_association import InventoryAchievementAssociationSchemaBase, InventoryAchievementAssociationSchemaFull

from .clusters.publication_cluster import PublicationClusterSchemaBase, PublicationClusterSchemaFull
from .clusters.group import ClusterGroupSchemaBase, ClusterGroupSchemaFull
from .clusters.level import ClusterLevelSchemaBase, ClusterLevelSchemaFull
from .clusters.topic import ClusterTopicSchemaBase, ClusterTopicSchemaFull

from .collection import CollectionSchemaBase, CollectionSchemaFull

from .sdg_ranks import SDGRankSchemaBase, SDGRankSchemaFull, UsersSDGRankSchemaBase

print("Export all models")
# Export all models for external use
__all__ = [
    "UserDataSchemaBase",
    "UserDataSchemaFull",
    "TokenDataSchemaBase",
    "TokenDataSchemaFull",
    "LoginSchemaBase",
    "LoginSchemaFull",

    "SDGTargetSchemaBase",
    "SDGTargetSchemaFull",

    "SDGGoalSchemaBase",
    "SDGGoalSchemaFull",

    "UserSchemaBase",
    "UserSchemaFull",

    "AdminSchemaBase",
    "AdminSchemaFull",

    "ExpertSchemaBase",
    "ExpertSchemaFull",

    "GroupSchemaBase",
    "GroupSchemaFull",

    "LabelerSchemaBase",
    "LabelerSchemaFull",

    "AuthorSchemaBase",
    "AuthorSchemaFull",

    "PublicationSchemaBase",
    "PublicationSchemaFull",

    "FacultySchemaBase",
    "FacultySchemaFull",

    "InstituteSchemaBase",
    "InstituteSchemaFull",

    "DivisionSchemaBase",
    "DivisionSchemaFull",

    "DimensionalityReductionSchemaBase",
    "DimensionalityReductionSchemaFull",

    "SDGPredictionSchemaBase",
    "SDGPredictionSchemaFull",

    "SDGTargetPredictionSchemaBase",
    "SDGTargetPredictionSchemaFull",

    "SDGLabelSummarySchemaBase",
    "SDGLabelSummarySchemaFull",

    "SDGLabelHistorySchemaBase",
    "SDGLabelHistorySchemaFull",

    "SDGLabelDecisionSchemaBase",
    "SDGLabelDecisionSchemaFull",

    "SDGUserLabelSchemaBase",
    "SDGUserLabelSchemaFull",

    "SDGLabelDistribution", # Non-entity-derived
    "UserVotingDetails",  # Non-entity-derived
    "SDGUserLabelStatisticsSchema",  # Non-entity-derived


    "VoteSchemaBase",
    "VoteSchemaFull",

    "AnnotationSchemaBase",
    "AnnotationSchemaFull",

    "SDGCoinWalletHistorySchemaBase",
    "SDGCoinWalletHistorySchemaFull",

    "SDGCoinWalletSchemaBase",
    "SDGCoinWalletSchemaFull",

    "SDGXPBankHistorySchemaBase",
    "SDGXPBankHistorySchemaFull",

    "SDGXPBankSchemaBase",
    "SDGXPBankSchemaFull",

    "FactSchemaBase",
    "FactSchemaFull",

    "SummarySchemaBase",
    "SummarySchemaFull",


    "AchievementSchemaBase",
    "AchievementSchemaFull",

    "InventorySchemaBase",
    "InventorySchemaFull",

    "InventoryAchievementAssociationSchemaBase",
    "InventoryAchievementAssociationSchemaFull",


    "PublicationClusterSchemaBase",
    "PublicationClusterSchemaFull",

    "ClusterGroupSchemaBase",
    "ClusterGroupSchemaFull",
    "ClusterLevelSchemaBase",
    "ClusterLevelSchemaFull",
    "ClusterTopicSchemaBase",
    "ClusterTopicSchemaFull",

    "CollectionSchemaBase",
    "CollectionSchemaFull",

    "SDGRankSchemaBase",
    "SDGRankSchemaFull",
    "UsersSDGRankSchemaBase" # Non-entity-derived
]

# Black magic below:

# Errors like:
# api  |   File "/usr/local/lib/python3.10/site-packages/pydantic/_internal/_mock_val_ser.py", line 58, in _get_built
# api  |     raise PydanticUserError(self._error_message, code=self._code)
# api  | pydantic.errors.PydanticUserError: `TypeAdapter[typing.Annotated[schemas.annotation.AnnotationSchemaFull, FieldInfo(annotation=AnnotationSchemaFull, required=True)]]`
# is not fully defined; you should define `typing.Annotated[schemas.annotation.AnnotationSchemaFull, FieldInfo(annotation=AnnotationSchemaFull, required=True)]`
# and all referenced types, then call `.rebuild()` on the instance.

# Resolve forward references for schemas
# Rebuild models to resolve forward references
SDGXPBankSchemaBase.model_rebuild()
SDGXPBankSchemaFull.model_rebuild()
SDGXPBankHistorySchemaBase.model_rebuild()
SDGXPBankHistorySchemaFull.model_rebuild()

PublicationSchemaBase.model_rebuild()
PublicationSchemaFull.model_rebuild()

CollectionSchemaBase.model_rebuild()
CollectionSchemaFull.model_rebuild()

SDGGoalSchemaBase.model_rebuild()
SDGGoalSchemaFull.model_rebuild()
SDGTargetSchemaBase.model_rebuild()
SDGTargetSchemaFull.model_rebuild()

SDGCoinWalletSchemaBase.model_rebuild()
SDGCoinWalletSchemaFull.model_rebuild()
SDGXPBankHistorySchemaBase.model_rebuild()
SDGXPBankHistorySchemaFull.model_rebuild()

AnnotationSchemaBase.model_rebuild()
AnnotationSchemaFull.model_rebuild()
VoteSchemaBase.model_rebuild()
VoteSchemaFull.model_rebuild()


SDGLabelSummarySchemaBase.model_rebuild()
SDGLabelSummarySchemaFull.model_rebuild()
SDGLabelHistorySchemaBase.model_rebuild()
SDGLabelHistorySchemaFull.model_rebuild()
SDGLabelDecisionSchemaBase.model_rebuild()
SDGLabelDecisionSchemaFull.model_rebuild()
SDGUserLabelSchemaBase.model_rebuild()
SDGUserLabelSchemaFull.model_rebuild()
SDGLabelDistribution.model_rebuild()
UserVotingDetails.model_rebuild()
SDGUserLabelStatisticsSchema.model_rebuild()


UserSchemaBase.model_rebuild()
UserSchemaFull.model_rebuild()
SDGRankSchemaBase.model_rebuild()
SDGRankSchemaFull.model_rebuild()
UsersSDGRankSchemaBase.model_rebuild()


print("Finished rebuilding schemas")
