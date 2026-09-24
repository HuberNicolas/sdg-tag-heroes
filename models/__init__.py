from .achievement import Achievement
from .annotation import Annotation
from .associations import (
    publication_authors_association,
    sdg_label_decision_user_label_association,
    user_group_association,
)
from .base import Base
from .clusters.group import ClusterGroup
from .clusters.level import ClusterLevel
from .clusters.publication_cluster import PublicationCluster
from .clusters.topic import ClusterTopic
from .collection import Collection
from .fact import Fact
from .inventory import Inventory
from .inventory_achievement_association import InventoryAchievementAssociation
from .publications.author import Author
from .publications.dimensionality_reduction import DimensionalityReduction
from .publications.division import Division
from .publications.faculty import Faculty
from .publications.institute import Institute
from .publications.publication import Publication
from .sdg_coin_wallet import SDGCoinWallet
from .sdg_coin_wallet_history import SDGCoinWalletHistory
from .sdg_label_decision import SDGLabelDecision
from .sdg_label_history import SDGLabelHistory
from .sdg_label_summary import SDGLabelSummary
from .sdg_prediction import SDGPrediction
from .sdg_ranks import SDGRank
from .sdg_target_prediction import SDGTargetPrediction
from .sdg_user_label import SDGUserLabel
from .sdg_xp_bank import SDGXPBank
from .sdg_xp_bank_history import SDGXPBankHistory
from .sdgs.goal import SDGGoal
from .sdgs.target import SDGTarget
from .summary import Summary
from .users.admin import Admin
from .users.expert import Expert
from .users.group import Group
from .users.labeler import Labeler
from .users.user import User
from .vote import Vote

# Export all models for external use
__all__ = [
    "Base",
    "User",
    "Admin",
    "Expert",
    "Labeler",
    "Group",
    "user_group_association",
    "Annotation",
    "SDGUserLabel",
    "Vote",
    "SDGLabelDecision",
    "SDGLabelHistory",
    "SDGLabelSummary",
    "SDGPrediction",
    "SDGTargetPrediction",
    "sdg_label_decision_user_label_association",
    "Author",
    "Division",
    "Institute",
    "Faculty",
    "DimensionalityReduction",
    "Publication",
    "publication_authors_association",
    "SDGGoal",
    "SDGTarget",
    "ClusterGroup",
    "ClusterLevel",
    "ClusterTopic",
    "PublicationCluster",
    "Inventory",
    "Achievement",
    "InventoryAchievementAssociation",
    "Fact",
    "Summary",
    "SDGXPBank",
    "SDGCoinWallet",
    "SDGXPBankHistory",
    "SDGCoinWalletHistory",
    "SDGRank",
]
