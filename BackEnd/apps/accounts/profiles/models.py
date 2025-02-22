from django.db import models
from django.conf import settings
from basemodels.models import BaseAddressWithBaseModel
from django.utils.translation import gettext
from core.constants.choices import COUNTRY_CHOICES, STATE_CHOICES, PROFILE_POSITION_CHOICES, PROFILE_DEPARTMENT_CHOICES



class Profile(BaseAddressWithBaseModel):
    """
    Profile model for extending user information.
    
    This model centralizes user profile information, combining relevant data
    from both NormalUser and Employeer models while adding new profile-specific fields.
    
    Fields:
        user (OneToOneField): Associated user account
        bio (TextField): User biography or description
        birth_date (DateField): User's birth date
        position (CharField): Current job position
        department (CharField): Department in the company
        avatar (ImageField): Profile picture
        social_links (JSONField): Social media links
        preferences (JSONField): User interface preferences
        
    Inherits:
        BaseAddressWithBaseModel{
            id: UUIDField
            companie: ForeignKey to Companie
            phone: CharField
            email: EmailField
            address: CharField
            city: CharField
            state: CharField
            zip_code: CharField
            country: CharField
            created_at, updated_at: DateTimeField
            created_by, updated_by: ForeignKey
        }
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    bio = models.TextField(
        blank=True,
        help_text=gettext("A brief biography or description of the user")
    )
    birth_date = models.DateField(
        null=True,
        blank=True,
        help_text=gettext("Date of birth of the user")
    )
    position = models.CharField(
        max_length=100,
        blank=True,
        choices=PROFILE_POSITION_CHOICES,
        help_text=gettext("Current position of the user")
    )
    department = models.CharField(
        max_length=100,
        blank=True,
        choices=PROFILE_DEPARTMENT_CHOICES,
        help_text=gettext("Department of the user in the company")
    )
    avatar = models.ImageField(
        upload_to='profiles/avatars/',
        null=True,
        blank=True,
        help_text=gettext("Profile picture of the user")
    )
    social_links = models.JSONField(
        default=dict,
        blank=True,
        help_text=gettext("Social media links of the user")
    )
    preferences = models.JSONField(
        default=dict,
        blank=True,
        help_text=gettext("User interface preferences")
    )
    
    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'
        ordering = ['user__first_name', 'user__last_name']
        permissions = [
            ("view_own_profile", "Can view own profile"),
            ("edit_own_profile", "Can edit own profile"),
        ]

    def __str__(self):
        return f"Profile of {self.user.get_full_name() or self.user.email}"

    def get_full_name(self):
        """Returns user's full name or email if name not set."""
        return self.user.get_full_name() or self.user.email

    @property
    def age(self):
        """Calculate age based on birth_date."""
        if self.birth_date:
            from datetime import date
            today = date.today()
            return today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
            )
        return None

    def get_social_link(self, platform):
        """Get social media link for specific platform."""
        return self.social_links.get(platform)

    def set_social_link(self, platform, url):
        """Set social media link for specific platform."""
        if not self.social_links:
            self.social_links = {}
        self.social_links[platform] = url
        self.save()

    
