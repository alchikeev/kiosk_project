import time

class SessionState:
    def __init__(self):
        self.language = "ru"
        self.operation = None
        self.page_count = 0
        self.status = "initialized"
        self.created_at = time.time()
        self.paid = False
        self.timeout = 300

    def is_expired(self):
        return (time.time() - self.created_at) > self.timeout

    def mark_paid(self):
        self.paid = True
        self.status = "paid"

    def to_dict(self):
        return {
            "language": self.language,
            "operation": self.operation,
            "page_count": self.page_count,
            "status": self.status,
            "created_at": self.created_at,
            "paid": self.paid,
            "expired": self.is_expired()
        }
