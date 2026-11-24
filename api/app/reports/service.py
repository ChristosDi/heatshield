"""Report rules: calculate the dashboard numbers when they are asked for, by calling the other features' services."""
from ..requests import service as requests_service

# Which request statuses count towards each dashboard number. Every status is in exactly one group.
OUTSTANDING = ("pending", "in_progress")
COMPLETED = ("completed",)
REJECTED = ("rejected",)


def request_counts():
    """Count the support requests that are outstanding, completed and rejected, and in total."""
    by_status = requests_service.count_by_status()

    return {
        "outstanding": sum(by_status[status] for status in OUTSTANDING),
        "completed": sum(by_status[status] for status in COMPLETED),
        "rejected": sum(by_status[status] for status in REJECTED),
        "total": sum(by_status.values()),
    }