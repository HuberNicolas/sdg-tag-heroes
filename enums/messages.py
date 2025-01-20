from enum import Enum


class MessageEnum(str, Enum):
    get_sin_failed = "Get single resource failed"
    get_sin_successful = "Get single resource successful"
    get_col_failed = "Get collection resource failed"
    get_col_partially_successful = "Get collection partially successful"
    get_col_successful = "Get collection resource successful"
    patch_col_successful = "Patch collection completely successful"
    patch_col_partially_successful = "Patch collection partially successful"
    patch_col_failed = "Patch collection failed"
    post_col_partially_successful = "Post collection partially successful"
    post_col_successful = "Post collection successful"
    post_col_failed = "Post collection failed"
    post_col_empty_successful = "Post collection (empty) successfully"
