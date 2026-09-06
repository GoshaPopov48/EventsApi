class EventProviderError(Exception):
    pass


class DomainError(Exception):
    """Base exception for business logic."""


class EventNotFound(DomainError):
    def __init__(self):
        super().__init__("Event not found")


class EventNotPublished(DomainError):
    def __init__(self):
        super().__init__("Event not published")


class RegistrationClosed(DomainError):
    def __init__(self):
        super().__init__("Registration is closed")


class EventAlreadyStarted(DomainError):
    def __init__(self):
        super().__init__("Event has already started")


class SeatNotAvailable(DomainError):
    def __init__(self):
        super().__init__("Seat is not available")


class TicketNotFound(DomainError):
    def __init__(self):
        super().__init__("Ticket not found")


class TicketEventMismatch(DomainError):
    def __init__(self):
        super().__init__("Ticket does not belong to this event")


class RegistrationError(DomainError):
    def __init__(self, message: str):
        super().__init__(message)


class SyncError(DomainError):
    def __init__(self, message: str = "Synchronization failed"):
        super().__init__(message)
