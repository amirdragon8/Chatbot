
import json
import re
from django.contrib import messages
from datetime import datetime, timedelta
from django.utils.encoding import force_str
from authentification.models import CustomUser, VolunteerProfile
from chat.models import Task


def get_current_time():
    return datetime.now().strftime("%d %B %Y")

def extract_user_schema(model):
    """
    Dynamically extract the schema of a model with field names and descriptions,
    ensuring that the fields are in a specific order and relevant ones are included.
    """
    excluded_fields = [
        "id", "is_superuser", "last_login", "is_staff",
        "is_active", "date_joined", "role"
    ]
    
    # Predefined order of fields
    field_order = ['username', 'email', 'password', 'first_name', 'last_name']
    
    schema = {}
    for field in model._meta.get_fields():
        if field.concrete and not field.is_relation and field.name not in excluded_fields:
            # Assign field description (help_text or default)
            schema[field.name] = force_str(field.help_text or "Enter your password")
    
    # Reorder schema according to `field_order`
    ordered_schema = {field: schema.get(field, " ") for field in field_order}
    
    return ordered_schema

def extract_and_create_user(request, ai_response: str, chat_history: list):
    """
    Extracts JSON from AI response, validates required fields, and creates a user.

    Parameters:
        request: The Django HTTP request object.
        ai_response (str): The full text response from the AI containing JSON fragments.
        chat_history (list): Chat history for rendering back in the template if errors occur.

    Returns:
        bool: True if a user was successfully created, False otherwise.
    """
    try:
        # Regex to extract JSON-like fragments
        json_pattern = r'({.*?})'
        json_fragments = re.findall(json_pattern, ai_response, re.DOTALL)
        
        for fragment in json_fragments:
            try:
                # Parse JSON fragment
                user_data = json.loads(fragment)

                # Validate required fields
                username = user_data.get('username')
                email = user_data.get('email')
                password = user_data.get('password')

                if not username or not email or not password:
                    messages.error(request, "Missing required fields in the AI response.")
                    chat_history.append({"role": "System error", "message": "Missing required fields in the AI response."})
                    continue  # Move to the next JSON fragment

                # Check if the username already exists
                if CustomUser.objects.filter(username=username).exists():
                    error_message = f"Username '{username}' already exists! Please choose another."
                    messages.error(request, error_message)
                    chat_history.append({"role": "System error", "message": error_message})
                    generate_helpful_ai_response(chat_history, "username")

                # Check if the email is already registered
                if CustomUser.objects.filter(email=email).exists():
                    error_message = f"Email '{email}' is already registered! Please use a different email."
                    messages.error(request, error_message)
                    chat_history.append({"role": "System error", "message": error_message})
                    generate_helpful_ai_response(chat_history, "email")

                # Create the user with fixed role 'VOLUNTEER'
                new_user = CustomUser.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=user_data.get('first_name'),
                    last_name=user_data.get('last_name'),
                    role="VOLUNTEER",
                )
                success_message = f"User '{username}' successfully created!"
                messages.success(request, success_message)
                chat_history.append({"role": "System message", "message": success_message})
                return True

            except json.JSONDecodeError:
                continue  # Skip invalid JSON fragments

        # If no valid user could be created
        messages.error(request, "No valid user data found in the AI response.")
        chat_history.append({"role": "System error", "message": "No valid user data found in the AI response."})
        return False

    except Exception as e:
        # Log the error and show a generic error message
        print(f"Error processing AI response: {e}")
        messages.error(request, "An error occurred while processing the AI response.")
        chat_history.append({"role": "System error", "message": "An unexpected error occurred while processing the request."})
        return False

def generate_helpful_ai_response(chat_history, error_type):
    """
    Generates a follow-up AI response to assist users in resolving errors.

    Parameters:
        chat_history (list): The current chat history.
        error_type (str): The type of error ('username' or 'email').
    """
    if error_type == "username":
        ai_message = "It seems the username you chose is already taken. Please provide a different username to proceed."
    elif error_type == "email":
        ai_message = "The email address you provided is already registered. Please provide a different email address."
    else:
        ai_message = "There was an issue with the provided information. Let's try again with corrected details."

    chat_history.append({"role": "ai", "message": ai_message})

def extract_task_schema(model):
    """
    Dynamically extract the schema of a Task model with field names and descriptions,
    ensuring that the fields are in a specific order and relevant ones are included.
    If a user is provided, the `created_by` field will be populated with the user's username.
    """
    excluded_fields = ["id", "created_at", "updated_at", "created_by_id"]  # Exclude fields like ID and timestamps
    
    # Predefined order of fields
    field_order = ['name', 'description', 'start_date', 'end_date']
    
    schema = {}
    for field in model._meta.get_fields():
        if field.concrete and not field.is_relation and field.name not in excluded_fields:
            # Assign field description (help_text or default)
            schema[field.name] = force_str(field.help_text or "No description available")
    
    # Reorder schema according to `field_order`
    ordered_schema = {field: schema.get(field, " ") for field in field_order}
    
    return ordered_schema

def extract_and_create_task(request, ai_response, chat_history):
    try:
        # Regex to extract JSON-like fragments
        json_pattern = r'\{.*?\}'
        json_fragments = re.findall(json_pattern, ai_response, re.DOTALL)

        print(f"Extracted JSON fragments: {json_fragments}")  # Debugging

        for fragment in json_fragments:
            try:
                task_data = json.loads(fragment.strip())
                print(f"Parsed JSON: {task_data}")  # Debugging
                name = task_data.get("name")
                description = task_data.get("description")
                start_date = task_data.get("start_date")
                end_date = task_data.get("end_date")
                # Validation logic...
                if not name or not description or not start_date or not end_date:
                    print("Validation failed. Missing required fields.")
                    break

                # Assume Task.objects.create() works as expected for now
                #print(f"Task created: {task_data}")
                new_task = Task.objects.create(
                    name= name,
                    description=description,
                    start_date= start_date,
                    end_date= end_date,
                    created_by=request.user,  # Set the current logged-in user as the creator
                )
                return {"success": True, "log_info": "Task created successfully."}

            except json.JSONDecodeError as e:
                print(f"JSON decoding failed: {e}")
                continue

        return {"success": False, "error_message": "No valid task data found."}
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {"success": False, "error_message": str(e)}
    

def extract_volunteer_profile_schema(model):
    """
    Dynamically extract the schema of the VolunteerProfile model with field names and descriptions,
    ensuring fields are included in a specific order and their help_text or default descriptions are used.
    """
    excluded_fields = ["id", "user"]  # Exclude fields like ID and user relationship

    # Predefined order of fields for better readability
    field_order = [
        "gender",
        "short_description",
        "date_of_birth",
        "interests",
        "goal_statement",
        "competencies_areas",
        "schedule"
    ]

    schema = {}
    for field in model._meta.get_fields():
        if field.concrete and not field.is_relation and field.name not in excluded_fields:
            # Add help_text or a default description if help_text is not available
            schema[field.name] = force_str(field.help_text or " ")

    # Handle special fields like interests, competencies_areas, and schedule
    schema["interests"] = "Tags representing areas of interest, e.g., 'Technology', 'Health'."
    schema["competencies_areas"] = (
        "A dictionary mapping FIELD_CHOICES to levels (0-3), e.g., "
        "{'ENVIRONMENT': 2, 'EDUCATION': 3}. "
        f"Available FIELD_CHOICES: {dict(model.FIELD_CHOICES)}."
    )
    schema["schedule"] = (
        "A dictionary mapping days of the week to available time slots, e.g., "
        "{'Monday': ['14:00-16:00'], 'Friday': ['10:00-12:00', '15:00-17:00']}. "
        f"Valid days: {[day[0] for day in model.DAYS_OF_WEEK]}."
    )

    # Reorder the schema based on the predefined order
    ordered_schema = {field: schema.get(field, " ") for field in field_order}

    return ordered_schema

def extract_and_create_volunteer_profile(request, ai_response, chat_history):
    try:
        # Regex to extract JSON-like fragments
        json_pattern = r'\{.*?\}'
        json_fragments = re.findall(json_pattern, ai_response, re.DOTALL)

        print(f"Extracted JSON fragments: {json_fragments}")  # Debugging

        for fragment in json_fragments:
            try:
                profile_data = json.loads(fragment.strip())
                print(f"Parsed JSON: {profile_data}")  # Debugging

                # Extract individual fields
                gender = profile_data.get("gender")
                short_description = profile_data.get("short_description")
                date_of_birth = profile_data.get("date_of_birth")
                interests = profile_data.get("interests", [])
                goal_statement = profile_data.get("goal_statement")
                competencies_areas = profile_data.get("competencies_areas", {})
                schedule = profile_data.get("schedule", {})

                # Validation logic
                if not gender or not date_of_birth or not competencies_areas or not schedule:
                    print("Validation failed. Missing required fields.")
                    break

                # Create or update the volunteer profile
                VolunteerProfile.objects.update_or_create(
                    user=request.user,  # Ensure the profile is linked to the current user
                    defaults={
                        "gender": gender,
                        "short_description": short_description,
                        "date_of_birth": date_of_birth,
                        "goal_statement": goal_statement,
                        "competencies_areas": competencies_areas,
                        "schedule": schedule,
                    },
                )

                # Update tags (interests)
                profile = VolunteerProfile.objects.get(user=request.user)
                profile.interests.set(interests)

                return {"success": True, "log_info": "Volunteer profile created or updated successfully."}

            except json.JSONDecodeError as e:
                print(f"JSON decoding failed: {e}")
                continue

        return {"success": False, "error_message": "No valid volunteer profile data found."}
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {"success": False, "error_message": str(e)}





