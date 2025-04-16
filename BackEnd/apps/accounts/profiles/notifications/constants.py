"""
Constants for Profile notifications.
"""

APP_NAME = 'PROFILES'

NOTIFICATION_TYPE = {
    'PROFILE_CREATED': 'profile_created',
    'PROFILE_UPDATED': 'profile_updated',
    'PROFILE_DELETED': 'profile_deleted',
    'AVATAR_UPDATED': 'avatar_updated'
}

NOTIFICATION_TITLES = {
    NOTIFICATION_TYPE['PROFILE_CREATED']: 'New Profile Created',
    NOTIFICATION_TYPE['PROFILE_UPDATED']: 'Profile Updated',
    NOTIFICATION_TYPE['PROFILE_DELETED']: 'Profile Deleted',
    NOTIFICATION_TYPE['AVATAR_UPDATED']: 'Profile Avatar Updated'
}

NOTIFICATION_MESSAGES = {
    NOTIFICATION_TYPE['PROFILE_CREATED']: 'New profile created for {user_name}',
    NOTIFICATION_TYPE['PROFILE_UPDATED']: 'Profile updated for {user_name}',
    NOTIFICATION_TYPE['PROFILE_DELETED']: 'Profile deleted for {user_name}',
    NOTIFICATION_TYPE['AVATAR_UPDATED']: 'Avatar updated for {user_name}'
}

SEVERITY_TYPES = {
    NOTIFICATION_TYPE['PROFILE_CREATED']: 'info',
    NOTIFICATION_TYPE['PROFILE_UPDATED']: 'info',
    NOTIFICATION_TYPE['PROFILE_DELETED']: 'warning',
    NOTIFICATION_TYPE['AVATAR_UPDATED']: 'info'
}

NOTIFICATION_PRIORITIES = {
    NOTIFICATION_TYPE['PROFILE_CREATED']: 'normal',
    NOTIFICATION_TYPE['PROFILE_UPDATED']: 'normal',
    NOTIFICATION_TYPE['PROFILE_DELETED']: 'high',
    NOTIFICATION_TYPE['AVATAR_UPDATED']: 'low'
}

RECIPIENT_TYPES = {
    'DEFAULT': ['Owner', 'CEO', 'Admin'],
    'PROFILE_ADMIN': ['Admin'],
    'HR': ['Manager', 'HR', 'Admin']
}