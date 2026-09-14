from datetime import datetime
from typing import Any, Dict


def send_notification(
    notification_type: str,
    payload: Dict[str, Any],
) -> bool:
    """
    Handle a prototype notification event.

    In the current CoCare prototype, notifications are logged
    locally rather than sent through an external notification
    service.

    Args:
        notification_type: Type of notification or escalation.
        payload: Information associated with the event.

    Returns:
        True if the notification event was processed.
        False if no notification was required.
    """

    if not notification_type or notification_type.lower() == "none":
        return False

    if payload is None:
        payload = {}

    timestamp = datetime.now().isoformat(timespec="seconds")

    notification_event = {
        "timestamp": timestamp,
        "type": notification_type,
        "payload": payload,
    }

    print("[CoCare Notification]")
    print(notification_event)

    return True
