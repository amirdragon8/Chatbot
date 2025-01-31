import json
from django.shortcuts import redirect, render
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse

from authentification.models import CustomUser, VolunteerProfile
from chat.decorators import role_required, unauthenticated_user
from chat.helpers import *
from chat.models import Task
from .ollama_api import generate_response
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages


# Create your views here.

@csrf_exempt
def chat_view(request):
    if request.method == "POST":
        user_input = request.POST.get("user_input")
        # Retrieve the chat history from the session
        chat_history = request.session.get("chat_history", [])

        # Build the full prompt for the AI model using the chat history
        prompt = ""
        for message in chat_history:
            if message['role'] == 'user':
                prompt += f"User: {message['message']}\n"
            elif message['role'] == 'ai':
                prompt += f"AI: {message['message']}\n"

        prompt += f"User: {user_input}\nAI:"

        # Generate the AI response
        ai_response = ""
        try:
            # Get AI response from the generate_response function (assuming it's a generator)
            for chunk in generate_response(prompt):
                ai_response += chunk
        except Exception as e:
            ai_response = "Sorry, there was an error generating the response."

        # Add the user message and AI response to the chat history
        chat_history.append({"role": "user", "message": user_input})
        chat_history.append({"role": "ai", "message": ai_response})

        # Store the updated chat history in the session
        request.session["chat_history"] = chat_history
        
        # Return the updated page with the chat history and the AI response
        return render(request, "chat.html", {"chat_history": chat_history})
    return render(request, "chat.html", {"chat_history": []})

@role_required('NPO_MANAGER')
@csrf_exempt
def form_view(request):
    chat_history = request.session.get("chat_history", [])
    response = render(request, "form-creation.html", {"chat_history": chat_history})
    if request.method == "POST":
        user_input = request.POST.get("user_input")
        task_schema = extract_task_schema(Task) 
        chat_history = request.session.get("chat_history", [])

        # Build the full prompt for the AI model using the chat history
        prompt = f'''In this chat your goal is help User to create task in Austrian voluntering portal. 
        Your role is to assist the user in providing and validating the following information:
        - **User Information**: {json.dumps(task_schema, indent=2)} 
        Note:
        1. Name and description should be correlated.
        2. Start date should not be earlier than {get_current_time()}.
        3. Start date should not be later than end date.
        4. End date should not be earlier than the start date.
        5. End date should not be later than the start date plus 5 years.
        6. Convert date for convenient format yourself if user send it other order
        7. When all fields are complete, output the finalized form in JSON format with the following phrasing:
        "There is final version of JSON form:" followed by the JSON data.

        Use the following chat history to guide your responses:
        '''
        for message in chat_history:
            if message['role'] == 'user':
                prompt += f"User: {message['message']}\n"
            elif message['role'] == 'ai':
                prompt += f"AI: {message['message']}\n"

        prompt += f"User: {user_input}\nAI:"

        # Generate the AI response
        ai_response = ""
        try:
            # Get AI response from the generate_response function (assuming it's a generator)
            for chunk in generate_response(prompt):
                ai_response += chunk
        except Exception as e:
            ai_response = "Sorry, there was an error generating the response."

        # Add the user message and AI response to the chat history
        chat_history.append({"role": "user", "message": user_input})
        chat_history.append({"role": "ai", "message": ai_response})

        # Store the updated chat history in the session
        request.session["chat_history"] = chat_history

        if "There is final version of JSON form:" in ai_response:
            result = extract_and_create_task(request, ai_response, chat_history)
            if result.get("success"):
                return redirect('chat:user_tasks', username=request.user.username)

        # Return the updated page with the chat history and the AI response
        return render(request, "form-creation.html", {"chat_history": chat_history})

    # Render the initial page with an chat history
    return response

@role_required('NPO_MANAGER')
def user_tasks_view(request, username):
    # Filter tasks by the CustomUser instance
    tasks = Task.objects.filter(created_by__username=username)
    return render(request, 'user_tasks.html', {'tasks': tasks, 'username': username})





@csrf_exempt
@unauthenticated_user
def register_view(request):
    chat_history = request.session.get("chat_history", [])
    response = render(request, "user-registration.html", {"chat_history": chat_history})

    if request.method == "POST":
        user_input = request.POST.get("user_input")
        user_schema = extract_user_schema(CustomUser)
        chat_history = request.session.get("chat_history", [])

        # Refined prompt to guide AI behavior
        prompt = f'''In this chat, your goal is to help the visitor create a user profile in the Austrian volunteering portal.
        Your role is to assist the user in providing and validating the following information:
        - **User Information**: {json.dumps(user_schema, indent=2)}
        Note:
        1. The user's role is fixed as 'Volunteer' and cannot be changed.
        2. Collect all fields from the user, validate their input for each field, and request corrections if needed. 
        The user needs to confirm their password twice (in two separate messages).
        3. When all fields are complete, output the finalized form in JSON format with the following phrasing:
           "There is final version of JSON form:" followed by the JSON data.
        4. If the system returns an error (e.g., duplicate username or email), provide suggestions to the user for resolving the issue.

        Use the following chat history to guide your responses:
        '''

        for message in chat_history:
            if message['role'] == 'user':
                prompt += f"User: {message['message']}\n"
            elif message['role'] == 'ai':
                prompt += f"AI: {message['message']}\n"

        prompt += f"User: {user_input}\nAI:"

        # Generate the AI response
        ai_response = ""
        try:
            for chunk in generate_response(prompt):
                ai_response += chunk
        except Exception as e:
            ai_response = f"Error generating response: {e}"

        # Add the user message and AI response to the chat history
        chat_history.append({"role": "user", "message": user_input})
        chat_history.append({"role": "ai", "message": ai_response})

        # Store the updated chat history in the session
        request.session["chat_history"] = chat_history

        # Detect and process the finalized JSON response
        if "There is final version of JSON form:" in ai_response:
            success = extract_and_create_user(request, ai_response, chat_history)
            if success:
                return redirect('authentification:signin')

        return render(request, "user-registration.html", {"chat_history": chat_history})

    # Render the initial page with chat history
    return response

@role_required('VOLUNTEER')
def volunteer_onboard_view(request):
    chat_history = request.session.get("chat_history", [])
    response = render(request, "vonboard.html", {"chat_history": chat_history})
    if request.method == "POST":
        user_input = request.POST.get("user_input")
        volunteer_schema = extract_volunteer_profile_schema(VolunteerProfile)
        chat_history = request.session.get("chat_history", [])
        prompt = f'''In this chat, your goal is to assist the user in creating their volunteer profile for the Austrian volunteering portal.
        Your role is to help the user provide and validate the following information:
        - **Volunteer Profile Schema**: {json.dumps(volunteer_schema, indent=2)}
        Note:
        1. The volunteer's user account is already linked, so you don't need to request user information. 
        You need to help to create Volunteer Profile for existing user
        2. Collect all fields from the user, validate their input for each field, and request corrections if needed. 
        Field of interests (also called competences) is restricted by provided schema choices. Ask user to select one or more options from them 
        and indicate level of competence(interest) from 0 to 3.
        3. When all fields are complete, output the finalized form in JSON format with the following phrasing:
           "There is final version of JSON form:" followed by the JSON data.
        4. If the system encounters an error (e.g., invalid data), provide actionable suggestions for resolving the issue.

        Use the following chat history to guide your responses:
        '''

        for message in chat_history:
            if message['role'] == 'user':
                prompt += f"User: {message['message']}\n"
            elif message['role'] == 'ai':
                prompt += f"AI: {message['message']}\n"

        prompt += f"User: {user_input}\nAI:"

         # Generate the AI response
        ai_response = ""
        try:
            for chunk in generate_response(prompt):
                ai_response += chunk
        except Exception as e:
            ai_response = f"Error generating response: {e}"

        # Add the user message and AI response to the chat history
        chat_history.append({"role": "user", "message": user_input})
        chat_history.append({"role": "ai", "message": ai_response})

        # Store the updated chat history in the session
        request.session["chat_history"] = chat_history

        if "There is final version of JSON form:" in ai_response:
            success = extract_and_create_volunteer_profile(request, ai_response, chat_history)
            if success:
                return redirect('authentification:index')  # Redirect to the main page after successful onboarding

        return render(request, "vonboard.html", {"chat_history": chat_history})
    return render(request, "vonboard.html")







def show_schema(request):
    user_schema = extract_user_schema(CustomUser)
    user_schema_str = f"{user_schema}"
    task_schema = extract_task_schema(Task) 
    task_schema_str =  f'''{task_schema}'''
    volunteer_schema = extract_volunteer_profile_schema(VolunteerProfile)
    volunteer_schema_str = f'''{volunteer_schema}'''
    return HttpResponse(user_schema_str+task_schema_str+volunteer_schema_str)

def create_and_show_user(request):
    # Simulate the incoming user data, or get it from POST request
    username = 'newuser'
    email = 'newuser@example.com'
    password = 'securepassword'
    user_data = {
        'first_name': 'John',
        'last_name': 'Doe'
    }

    # Create the user
    new_user = CustomUser.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=user_data.get('first_name'),
        last_name=user_data.get('last_name'),
        role="VOLUNTEER",
    )

    # Prepare the data to display
    user_info = {
        'username': new_user.username,
        'email': new_user.email,
        'first_name': new_user.first_name,
        'last_name': new_user.last_name,
        'role': new_user.role,
    }
# Option 1: Return the user data as a simple HttpResponse
    user_info_str = f"Username: {user_info['username']}<br>" \
                    f"Email: {user_info['email']}<br>" \
                    f"First Name: {user_info['first_name']}<br>" \
                    f"Last Name: {user_info['last_name']}<br>" \
                    f"Role: {user_info['role']}<br>"

    return HttpResponse(user_info_str)

def test_user_registration(request):
    """
    A simple Django view to handle user registration based on an AI response containing JSON.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the user registration template with appropriate messages.
    """
    # Simulate an example AI response
    ai_response = """
    Here is the user JSON:
    {
        "username": "john_doe",
        "email": "john.doe@example.com",
        "password": "securepassword123",
        "first_name": "John",
        "last_name": "Doe"
    } if "There is final version of JSON form: 
    """
    
    # Simulate chat history (you can replace this with actual chat history from your application)
    chat_history = "Chat history example content"
    if "There is final version of JSON form:" in ai_response:
        return extract_and_create_user(request, ai_response, chat_history)
    # Call the function to process the AI response and create a user
    return HttpResponse('failed test')


def create_and_show_task(request):
    # Simulate incoming task data, or get it from POST request
    name = "New Task"
    description = "This is a description of the new task."
    start_date = "2025-01-05"
    end_date = "2025-01-05"

    # Create the task
    new_task = Task.objects.create(
        name=name,
        description=description,
        start_date=start_date,
        end_date=end_date,
        created_by=request.user  # Assign the logged-in user as the creator
    )

    # Prepare the task data to display
    task_info = {
        'name': new_task.name,
        'description': new_task.description,
        'start_date': new_task.start_date,
        'end_date': new_task.end_date,
        'created_by': new_task.created_by.username,
    }

    # Option 1: Return the task data as a simple HttpResponse
    task_info_str = f"Task Name: {task_info['name']}<br>" \
                    f"Description: {task_info['description']}<br>" \
                    f"Start Date: {task_info['start_date']}<br>" \
                    f"End Date: {task_info['end_date']}<br>" \
                    f"Created By: {task_info['created_by']}<br>"

    return HttpResponse(task_info_str)

def test_task_creation(request):
    """
    Debugging-enabled Django view to handle task creation.
    """
    ai_response = """
    {
        "name": "Task 1",
        "description": "This is the first task description",
        "start_date": "2025-01-10",
        "end_date": "2025-01-10"
    } Here is the task JSON:
    """

    chat_history = []

    if "Here is the task JSON:" in ai_response:
        result = extract_and_create_task(request, ai_response, chat_history)
        print(f"Result from extract_and_create_task: {result}")  # Debugging

        if result.get("success"):
            return HttpResponse("Task creation succeeded.")
        else:
            error_message = result.get("error_message", "Unknown error occurred.")
            log_info = result.get("log_info", "No additional log information.")
            return HttpResponse(f"Task creation failed.<br>Error: {error_message}<br>Log: {log_info}")

    return HttpResponse("Invalid AI response format.")
