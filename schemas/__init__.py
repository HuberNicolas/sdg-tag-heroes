# Note: This was/should be deactivated as the circular imports are hard to handle for automatic schema generation via pydantic-to-typescript
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
]

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
