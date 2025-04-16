from django.db import models
from enum import Enum
import logging

logger = logging.getLogger(__name__)

# Create your models here.

class MovementType(str, Enum):
    INFLOW = 'Entry'
    OUTFLOW = 'Exit'
    TRANSFER = 'Transfer'
    
    @classmethod
    @property
    def values(cls):
        return [member.value for member in cls]

class MovementStatus(str, Enum):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    CANCELLED = 'cancelled'
    COMPLETED = 'completed'
    
    @classmethod
    @property
    def values(cls):
        return [member.value for member in cls]