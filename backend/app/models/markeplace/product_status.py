import enum


class ProductStatus(str, enum.Enum):
    draft = "draft"  # created, no data processed yet
    processing = "processing"  # pipeline is computing/generating data
    active = "active"  # data ready, purchasable
    failed = "failed"  # processing failed
