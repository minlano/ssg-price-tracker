from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Product:
    id: Optional[int]
    name: str
    url: str
    current_price: int
    created_at: Optional[datetime] = None

@dataclass
class PriceLog:
    id: Optional[int]
    product_id: int
    price: int
    logged_at: Optional[datetime] = None

@dataclass
class Alert:
    id: Optional[int]
    product_id: int
    user_email: str
    target_price: int
    is_active: bool = True