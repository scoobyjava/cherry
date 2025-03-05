import os

# Dynamic Guardrail Configuration
GUARDRAILS_ENABLED = os.getenv('GUARDRAILS_ENABLED', 'True') == 'True'
MAJOR_SYSTEM_CHANGE_TYPES = ['core_update', 'infrastructure_change']

def requires_explicit_approval(change_type: str, approved: bool = False) -> bool:
    """
    Returns True if the change is a major system change and hasn't been explicitly approved.
    """
    if GUARDRAILS_ENABLED and change_type in MAJOR_SYSTEM_CHANGE_TYPES and not approved:
        return True
    return False
