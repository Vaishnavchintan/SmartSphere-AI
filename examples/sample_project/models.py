"""
Data models and repository definitions.
"""
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class User:
    id: int
    username: str
    email: str
    is_admin: bool = False

@dataclass
class Order:
    id: str
    amount: float
    status: str
    user_id: int
    discount_code: Optional[str] = None
    final_price: Optional[float] = None
    requires_manual_approval: bool = False
