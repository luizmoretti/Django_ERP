"""
Profile notification handlers
"""
import logging
from apps.notifications.base import BaseNotificationHandler
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from ..models import Profile
from .constants import (
    APP_NAME,
    NOTIFICATION_TYPE,
    NOTIFICATION_TITLES,
    NOTIFICATION_MESSAGES,
    SEVERITY_TYPES,
    RECIPIENT_TYPES
)

logger = logging.getLogger(__name__)

class ProfileNotificationHandler(BaseNotificationHandler):
    """Handler for profile-related notifications."""
    
    @staticmethod
    def _get_profile_context(profile):
        """
        Get common context data for profile notifications
        
        Args:
            profile (Profile): Profile instance
            
        Returns:
            dict: Context data for notification
        """
        return {
            'profile_id': str(profile.id),
            'user_name': profile.user.get_full_name(),
            'position': profile.position,
            'department': profile.department
        }
    
    @staticmethod
    @receiver(post_save, sender=Profile)
    def notify_profile_status(sender, instance, created, **kwargs):
        """
        Handle notifications for profile creation and updates
        """
        if not instance:
            return
            
        handler = ProfileNotificationHandler()
        context = handler._get_profile_context(instance)
        
        if created:
            handler.notify_profile_created(instance, context)
        else:
            handler.notify_profile_updated(instance, context)
    
    def notify_profile_created(self, profile, context=None):
        """
        Send notification for profile creation
        
        Args:
            profile: Created profile instance
            context: Optional pre-built context
        """
        if context is None:
            context = self._get_profile_context(profile)
            
        recipients = self.get_recipients_by_type(*RECIPIENT_TYPES['DEFAULT'])
        recipient_ids = [str(user.id) for user in recipients]
        
        self.send_to_recipients(
            recipient_ids=recipient_ids,
            title=NOTIFICATION_TITLES[NOTIFICATION_TYPE['PROFILE_CREATED']],
            message=NOTIFICATION_MESSAGES[NOTIFICATION_TYPE['PROFILE_CREATED']] % context,
            app_name=APP_NAME,
            notification_type=SEVERITY_TYPES[NOTIFICATION_TYPE['PROFILE_CREATED']],
            data=context
        )
    
    def notify_profile_updated(self, profile, context=None):
        """
        Send notification for profile updates
        
        Args:
            profile: Updated profile instance
            context: Optional pre-built context
        """
        if context is None:
            context = self._get_profile_context(profile)
            
        recipients = self.get_recipients_by_type(*RECIPIENT_TYPES['DEFAULT'])
        recipient_ids = [str(user.id) for user in recipients]
        
        self.send_to_recipients(
            recipient_ids=recipient_ids,
            title=NOTIFICATION_TITLES[NOTIFICATION_TYPE['PROFILE_UPDATED']],
            message=NOTIFICATION_MESSAGES[NOTIFICATION_TYPE['PROFILE_UPDATED']] % context,
            app_name=APP_NAME,
            notification_type=SEVERITY_TYPES[NOTIFICATION_TYPE['PROFILE_UPDATED']],
            data=context
        )
    
    @staticmethod
    @receiver(post_delete, sender=Profile)
    def notify_profile_deleted_signal(sender, instance, **kwargs):
        """
        Handle notification for profile deletion
        """
        if not instance:
            return
            
        handler = ProfileNotificationHandler()
        context = handler._get_profile_context(instance)
        handler.notify_profile_deleted(instance, context)
    
    def notify_profile_deleted(self, profile, context=None):
        """
        Send notification for profile deletion
        
        Args:
            profile: Deleted profile instance
            context: Optional pre-built context
        """
        if context is None:
            context = self._get_profile_context(profile)
            
        recipients = self.get_recipients_by_type(*RECIPIENT_TYPES['DEFAULT'])
        recipient_ids = [str(user.id) for user in recipients]
        
        self.send_to_recipients(
            recipient_ids=recipient_ids,
            title=NOTIFICATION_TITLES[NOTIFICATION_TYPE['PROFILE_DELETED']],
            message=NOTIFICATION_MESSAGES[NOTIFICATION_TYPE['PROFILE_DELETED']] % context,
            app_name=APP_NAME,
            notification_type=SEVERITY_TYPES[NOTIFICATION_TYPE['PROFILE_DELETED']],
            data=context
        )
    
    def notify_avatar_updated(self, profile, context=None):
        """
        Send notification for avatar updates
        
        Args:
            profile: Profile instance with updated avatar
            context: Optional pre-built context
        """
        if context is None:
            context = self._get_profile_context(profile)
            
        recipients = self.get_recipients_by_type(*RECIPIENT_TYPES['DEFAULT'])
        recipient_ids = [str(user.id) for user in recipients]
        
        self.send_to_recipients(
            recipient_ids=recipient_ids,
            title=NOTIFICATION_TITLES[NOTIFICATION_TYPE['AVATAR_UPDATED']],
            message=NOTIFICATION_MESSAGES[NOTIFICATION_TYPE['AVATAR_UPDATED']] % context,
            app_name=APP_NAME,
            notification_type=SEVERITY_TYPES[NOTIFICATION_TYPE['AVATAR_UPDATED']],
            data=context
        )