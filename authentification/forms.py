
from django import forms
from .models import CustomUser, NPOManagerProfile, VolunteerProfile
from taggit.forms import TagWidget

class RegistrationForm(forms.ModelForm):
    username = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES, required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'role']

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        # Username validation
        if CustomUser.objects.filter(username=username).exists():
            self.add_error('username', "Username already exists! Please try another username.")
        if len(username) > 25:
            self.add_error('username', "Username must be under 25 characters!")
        if not username.isalnum():
            self.add_error('username', "Username must be alphanumeric!")

        # Email validation
        if CustomUser.objects.filter(email=email).exists():
            self.add_error('email', "Email already registered!")

        # Password validation
        if password != confirm_password:
            self.add_error('confirm_password', "Passwords didn't match!")
        return cleaned_data


class NPOManagerProfileForm(forms.ModelForm):
    class Meta:
        model = NPOManagerProfile
        fields = ['npo_name']


class VolunteerProfileForm(forms.ModelForm):
    class Meta:
        model = VolunteerProfile
        fields = '__all__'
        widgets = {
            'interests': TagWidget(),  # Widget for TaggableManager
        }
    # Predefine choices for interests and schedule
    FIELD_CHOICES = VolunteerProfile.FIELD_CHOICES
    DAYS_OF_WEEK = VolunteerProfile.DAYS_OF_WEEK
    TIME_SLOTS = VolunteerProfile.TIME_SLOTS

    # Override the `field_areas` field with custom widgets
    field_areas = forms.MultipleChoiceField(
        choices=FIELD_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        help_text="Select fields of interest and specify levels in the JSON below."
    )

    # Override the `schedule` field to display as a list of days and time slots
    # schedule = forms.MultipleChoiceField(
    #     #widget=forms.CheckboxSelectMultiple(attrs={'class': 'schedule-checkbox'}),
    #     widget=forms.HiddenInput(),
    #     help_text="Select time slots for each day."
    # )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Dynamically create the checkboxes for each day of the week and the corresponding time slots
        for day, _ in self.DAYS_OF_WEEK:
            time_slot_choices = [(time_slot, time_slot) for time_slot in self.TIME_SLOTS]
            self.fields[f'{day}_schedule'] = forms.MultipleChoiceField(
                choices=time_slot_choices,
                widget=forms.CheckboxSelectMultiple,
                required=False,
                label=f"{day} Schedule",
                help_text=f"Select time slots for {day}.",
            )


    def clean_field_areas(self):
        """
        Validate the field_areas data.
        """
        data = self.cleaned_data['field_areas']
        return {field: 0 for field in data}  # Default level to 0 for selected fields
