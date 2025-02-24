from django.db import models, transaction
from django.db.models import Sum
from django.core.exceptions import ValidationError
from enum import Enum
from core.cache import ( 
    invalidate_cache_key,
    invalidate_cache_pattern,
    get_cache_key,
)
from django.utils.translation import gettext
from basemodels.models import BaseModel
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
    PENDING = 'Pending'
    APPROVED = 'Approved'
    CANCELLED = 'Cancelled'
    
    @classmethod
    @property
    def values(cls):
        return [member.value for member in cls]

class Movement(BaseModel):
    """
    Central model for tracking all inventory movements
    """
    origin = models.CharField(
        max_length=50,
        help_text='Origin of the movement',
        blank=True,
        null=True,
    )
    destination = models.CharField(
        max_length=50,
        help_text='Destination of the movement',
        blank=True,
        null=True,
    )
    
    type = models.CharField(
        max_length=20,
        choices=[(t, t) for t in MovementType.values],
        help_text='Type of movement (Entry, Exit, Transfer)',
        blank=True,
        null=True,
    )
    data = models.JSONField(
        help_text='Data of the movement',
        blank=True,
        null=True,
    )
    status = models.CharField(
        max_length=20,
        choices=[(s, s) for s in MovementStatus.values],
        help_text='Current status of the movement',
        blank=True,
        null=True,
    )
    total_items = models.PositiveIntegerField(
        default=0,
        help_text='Total number of items in this movement',
        blank=True,
        null=True,
    )
    total_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text='Total value of items in this movement',
        blank=True,
        null=True,
    )
    date = models.DateTimeField(
        auto_now_add=True,
        help_text='Date when the movement occurred',
        blank=True,
        null=True,
    )
    
    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['type']),
            models.Index(fields=['status']),
            models.Index(fields=['date']),
            models.Index(fields=['data'])
        ]
    
    def __str__(self):
        return f"{self.type} - {self.status} - {self.date}"
    
    def _invalidate_caches(self):
        """Invalidate all caches related to this movement"""
        try:
            # Invalidate list cache
            list_key = get_cache_key(
                key_type='movements',
                id='list'
            )
            invalidate_cache_key(list_key, cache_alias='default')
            logger.info(f"[MOVEMENTS - MODEL]Invalidated list cache: {list_key}")
            
            # Invalidate detail cache
            detail_key = get_cache_key(
                key_type='movements',
                id=self.id
            )
            invalidate_cache_key(detail_key, cache_alias='default')
            logger.info(f"[MOVEMENTS - MODEL]Invalidated detail cache: {detail_key}")
            
        except Exception as e:
            logger.error(f"[MOVEMENTS - MODEL]Error invalidating caches for movement {self.id}: {str(e)}")
            # Don't raise the exception since this is a cache operation
    
    
    def save(self, *args, **kwargs):
        """Save with cache invalidation"""
        self._invalidate_caches()
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Delete with cache invalidation"""
        self._invalidate_caches()
        super().delete(*args, **kwargs)