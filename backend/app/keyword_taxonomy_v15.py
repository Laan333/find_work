"""Frozen v15 taxonomy for match-analysis category tags (LLM must pick from this set)."""

from __future__ import annotations

# Canonical slugs (EN + common RU transliterations where useful). Do not rename without a version bump.
MATCH_CATEGORY_TAXONOMY_V15: tuple[str, ...] = (
    "backend",
    "frontend",
    "fullstack",
    "mobile",
    "devops",
    "sre",
    "qa",
    "data_engineering",
    "data_science",
    "ml",
    "nlp",
    "security",
    "dba",
    "system_admin",
    "embedded",
    "game_dev",
    "python",
    "java",
    "kotlin",
    "scala",
    "go",
    "rust",
    "cpp",
    "csharp",
    "dotnet",
    "javascript",
    "typescript",
    "react",
    "vue",
    "angular",
    "node",
    "php",
    "ruby",
    "swift",
    "sql",
    "postgresql",
    "mysql",
    "mongodb",
    "redis",
    "kafka",
    "rabbitmq",
    "elasticsearch",
    "docker",
    "kubernetes",
    "terraform",
    "aws",
    "gcp",
    "azure",
    "linux",
    "microservices",
    "highload",
    "fintech",
    "ecommerce",
    "b2b",
    "b2c",
    "remote",
    "office",
    "hybrid",
    "english_b2",
    "english_c1",
    "team_lead",
    "management",
    "product",
    "analytics",
    "other",
)

_ALLOWED = frozenset(MATCH_CATEGORY_TAXONOMY_V15)

# Map common LLM synonyms / noise to canonical tags.
_CATEGORY_ALIASES: dict[str, str] = {
    "js": "javascript",
    "ts": "typescript",
    "py": "python",
    "k8s": "kubernetes",
    "kubernetess": "kubernetes",
    "postgres": "postgresql",
    "pg": "postgresql",
    "ml_engineering": "ml",
    "machine_learning": "ml",
    "datascience": "data_science",
    "data_scientist": "data_science",
    "full_stack": "fullstack",
    "full-stack": "fullstack",
    "бекенд": "backend",
    "фронтенд": "frontend",
    "фулстек": "fullstack",
}


def normalize_match_categories(raw: list[str], *, max_items: int = 8) -> list[str]:
    """Map free-form LLM labels onto the v15 taxonomy; drop unknowns; preserve order."""

    out: list[str] = []
    seen: set[str] = set()
    for item in raw:
        key = str(item).strip().lower().replace(" ", "_").replace("-", "_")
        if not key:
            continue
        key = _CATEGORY_ALIASES.get(key, key)
        if key not in _ALLOWED:
            continue
        if key in seen:
            continue
        seen.add(key)
        out.append(key)
        if len(out) >= max_items:
            break
    return out
