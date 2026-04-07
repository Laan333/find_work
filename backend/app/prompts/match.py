"""Compatibility shim — canonical prompts live in `app.prompts_v15_1`."""

from app.prompts_v15_1 import MATCH_ANALYSIS_SYSTEM, MATCH_ANALYSIS_USER_TEMPLATE

__all__ = ["MATCH_ANALYSIS_SYSTEM", "MATCH_ANALYSIS_USER_TEMPLATE"]
