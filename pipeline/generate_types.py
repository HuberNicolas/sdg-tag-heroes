import subprocess
from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
OUTPUT_DIR = PROJECT_ROOT / "types"

# Ensure the output directory exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def generate_typescript(schema_module: str, output_file_name: str):
    """Generate TypeScript for a specific schema module."""
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT)  # Add project root to PYTHONPATH

    output_path = OUTPUT_DIR / output_file_name

    subprocess.run([
        "poetry", "run", "pydantic2ts",  # Use Poetry to invoke pydantic2ts
        "--module", schema_module,
        "--output", str(output_path),
        "--json2ts-cmd", "pnpm exec json2ts"
    ], check=True, env=env)

    print(f"Generated TypeScript for {schema_module} -> {output_path}")


# Generate TypeScript definitions for specific schemas (pointing directly to schema files)
schemas_to_generate = [
    ("schemas.sdgs.target", "sdgs_target.ts"),
    ("schemas.sdgs.goal", "sdgs_goal.ts"),
    ("schemas.users.user", "users_user.ts"),
    ("schemas.users.admin", "users_admin.ts"),
    ("schemas.users.expert", "users_expert.ts"),
    ("schemas.users.labeler", "users_labeler.ts"),
    ("schemas.users.group", "users_group.ts"),
    ("schemas.author", "author.ts"),
    ("schemas.publication", "publication.ts"),
    ("schemas.faculty", "faculty.ts"),
    ("schemas.institute", "institute.ts"),
    ("schemas.division", "division.ts"),
    ("schemas.dimensionality_reduction", "dimensionality_reduction.ts"),
    ("schemas.sdg_prediction", "sdg_prediction.ts"),
    ("schemas.sdg_target_prediction", "sdg_target_prediction.ts"),
    ("schemas.sdg_label_summary", "sdg_label_summary.ts"),
    ("schemas.sdg_label_history", "sdg_label_history.ts"),
    ("schemas.sdg_label_decision", "sdg_label_decision.ts"),
    ("schemas.sdg_user_label", "sdg_user_label.ts"),
    ("schemas.vote", "vote.ts"),
    ("schemas.annotation", "annotation.ts"),
    ("schemas.sdg_coin_wallet_history", "sdg_coin_wallet_history.ts"),
    ("schemas.sdg_coin_wallet", "sdg_coin_wallet.ts"),
    ("schemas.sdg_xp_bank_history", "sdg_xp_bank_history.ts"),
    ("schemas.sdg_xp_bank", "sdg_xp_bank.ts"),
    ("schemas.fact", "fact.ts"),
    ("schemas.summary", "summary.ts"),
    ("schemas.achievement", "achievement.ts"),
    ("schemas.inventory", "inventory.ts"),
    ("schemas.inventory_achievement_association", "inventory_achievement_association.ts"),
    ("schemas.clusters.publication_cluster", "clusters_publication_cluster.ts"),
    ("schemas.clusters.group", "clusters_group.ts"),
    ("schemas.clusters.level", "clusters_level.ts"),
    ("schemas.clusters.topic", "clusters_topic.ts"),
]


for module, output in schemas_to_generate:
    try:
        print(f"Processing: {module}")
        generate_typescript(module, output)
    except subprocess.CalledProcessError as e:
        print(f"Failed to generate TypeScript for {module}: {e}")
