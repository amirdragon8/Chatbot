from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from taggit.managers import TaggableManager



class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('VOLUNTEER', 'Volunteer'),
        ('NPO_MANAGER', 'NPO Manager'),
    ]
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, blank=False, help_text="Role of the user")

    username = models.CharField(
        max_length=150,
        unique=True,
        help_text="Enter your unique username. It will be used to log in.",
    )
    email = models.EmailField(
        unique=True,
        help_text="Enter a valid email address. This will be used for communication.",
    )
    first_name = models.CharField(
        max_length=30,
        blank=False,
        help_text="Enter your first name.",
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
        help_text="Enter your last name.",
    )
    def __str__(self):
        return self.username
    

class NPOManagerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="npo_manager_profile")
    npo_name = models.CharField(max_length=255, blank=False, help_text="Name of the Non-Profit Organization")

    def __str__(self):
        return f"{self.user.username}'s NPO Manager Profile"



class VolunteerProfile(models.Model):
    # Predefined FIELD_CHOICES categories
    FIELD_CHOICES = [
        ('ENVIRONMENT', 'Environmental Protection'),
        ('EDUCATION', 'Education'),
        ('HEALTH', 'Health & Wellness'),
        ('ARTS', 'Arts & Culture'),
        ('TECH', 'Technology'),
        ('OTHER', 'Other'),
    ]

    # Predefined days of the week
    DAYS_OF_WEEK = [
        ("Monday", "Monday"),
        ("Tuesday", "Tuesday"),
        ("Wednesday", "Wednesday"),
        ("Thursday", "Thursday"),
        ("Friday", "Friday"),
        ("Saturday", "Saturday"),
        ("Sunday", "Sunday"),
    ]

    # Predefined time slots (in 24-hour format)
    TIME_SLOTS = [
        "00:00-01:00",
        "01:00-02:00",
        "02:00-03:00",
        "03:00-04:00",
        "04:00-05:00",
        "05:00-06:00",
        "06:00-07:00",
        "07:00-08:00",
        "08:00-09:00",
        "09:00-10:00",
        "10:00-11:00",
        "11:00-12:00",
        "12:00-13:00",
        "13:00-14:00",
        "14:00-15:00",
        "15:00-16:00",
        "16:00-17:00",
        "17:00-18:00",
        "18:00-19:00",
        "19:00-20:00",
        "20:00-21:00",
        "21:00-22:00",
        "22:00-23:00",
        "23:00-00:00",
    ]


    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="volunteer_profile",
    )
    gender = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], null=True, blank=True)
    short_description = models.TextField(max_length=500, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    interests = TaggableManager(help_text="Tags representing areas of interest.")
    goal_statement = models.TextField(max_length=1000, blank=True, help_text="Describe your goals or motivations.")

    # Interest areas with levels (0-3)
    competencies_areas = models.JSONField(
        default=dict,
        help_text="A dictionary mapping interests to their levels (e.g., {'ENVIRONMENT': 2, 'EDUCATION': 3}).",
    )

    # Schedule: days mapped to available time slots
    schedule = models.JSONField(
        default=dict,
        help_text=(
            "A dictionary mapping days to time ranges (e.g., "
            "{'Monday': ['14:00-16:00'], 'Friday': ['10:00-12:00', '15:00-17:00']})."
        ),
    )


    def clean(self):
        """
        Validate competencies_areas and schedule for correct format and values.
        """
        # Validate competencies_areas
        for interest in self.competencies_areas:
            if interest not in dict(self.FIELD_CHOICES):
                raise ValidationError(f"Invalid interest: {interest}. Must be one of {list(dict(self.FIELD_CHOICES).keys())}.")
            # Setting default level to 0 since the level isn't directly being set via checkboxes.
            self.competencies_areas[interest] = 0  # Default level to 0 for simplicity in the validation.
        # Validate schedule
        valid_days = [day[0] for day in self.DAYS_OF_WEEK]
        for day, times in self.schedule.items():
            if day not in valid_days:
                raise ValidationError(f"Invalid day: {day}. Must be one of {valid_days}.")
            for time_range in times:
                if not self._is_valid_time_range(time_range):
                    raise ValidationError(f"Invalid time range: {time_range}. Must be in 'HH:MM-HH:MM' format.")



    def _is_valid_time_range(self, time_range):
        """
        Helper method to validate a time range string (e.g., '14:00-16:00').
        """
        try:
            start, end = time_range.split('-')
            start_hour, start_minute = map(int, start.split(':'))
            end_hour, end_minute = map(int, end.split(':'))
            return (
                0 <= start_hour < 24 and
                0 <= start_minute < 60 and
                0 <= end_hour < 24 and
                0 <= end_minute < 60 and
                (start_hour, start_minute) < (end_hour, end_minute)
            )
        except (ValueError, AttributeError):
            return False




    def __str__(self):
        return f"{self.user.username}'s Volunteer Profile"




