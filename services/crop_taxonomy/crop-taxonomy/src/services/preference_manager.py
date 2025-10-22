from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from uuid import UUID

class FarmerPreferenceManager:
    """Comprehensive farmer preference storage"""

    def __init__(self, db: Session):
        self.db = db
