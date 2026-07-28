import enum


class StripeConnectStatus(str, enum.Enum):
    connected = "connected"
    pending = "pending"
    not_connected = "not_connected"
