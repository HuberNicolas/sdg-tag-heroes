from .base import Base

from .users.user import User
from .users.admin import Admin
from .users.expert import Expert
from .users.labeler import Labeler
from .users.group import Group

from .annotation import Annotation
from .sdg_user_label import SDGUserLabel
from .vote import Vote
from .sdg_label_decision import SDGLabelDecision
from .sdg_label_history import SDGLabelHistory
from .sdg_label_summary import SDGLabelSummary
from .sdg_prediction import SDGPrediction
from .sdg_target_prediction import SDGTargetPrediction

from .associations import sdg_label_decision_user_label_association
from .associations import user_group_association


from .publications.author import Author
from .publications.division import Division
from .publications.institute import Institute
from .publications.faculty import  Faculty
from .publications.dimensionality_reduction import DimensionalityReduction
from .publications.publication import Publication

from .sdg.sdg_goal import SDGGoal
from .sdg.sdg_target import SDGTarget

from .sdg.clusters.group import ClusterGroup
from .sdg.clusters.level import ClusterLevel
from .sdg.clusters.topic import ClusterTopic
from .sdg.clusters.publication_cluster import PublicationCluster


from .inventory import Inventory
from .achievement import Achievement
from .inventor_achievement_association import InventoryAchievementAssociation

from .fact import Fact
from .summary import Summary

from .sdg_xp_bank import SDGXPBank
from .sdg_coin_wallet import SDGCoinWallet

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
]
