import logging

logger = logging.getLogger("CherryEscalation")


def escalate_issue(reason: str, steps: str, doc_link: str, channel: str = "CLI"):
    """
    Send escalation message with actionable instructions.
    - reason: Why user intervention is needed.
    - steps: Steps/settings to fix the issue.
    - doc_link: Link to documentation or next steps.
    - channel: Communication channel (CLI or UI).
    """
    message = (
        f"Escalation Alert: {reason}\n"
        f"Action Required: {steps}\n"
        f"Documentation: {doc_link}\n"
        "Please address the issue promptly."
    )
    if channel.upper() == "CLI":
        print(message)
    elif channel.upper() == "UI":
        logger.info("UI escalation: " + message)
    else:
        logger.error("Unknown escalation channel, defaulting to CLI")
        print(message)
