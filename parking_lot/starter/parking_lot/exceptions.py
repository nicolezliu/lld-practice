class ParkingLotError(Exception):
    """Base class for all parking lot errors."""


class ParkingFullError(ParkingLotError):
    """No spot available that fits the vehicle."""


class VehicleAlreadyParkedError(ParkingLotError):
    """A vehicle with this license plate is already in the lot."""


class InvalidTicketError(ParkingLotError):
    """Ticket id is unknown or has already been used."""
