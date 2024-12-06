import json
from django.shortcuts import render
from django.http import JsonResponse, StreamingHttpResponse
from .ollama_api import generate_response
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

@csrf_exempt
def chat_view(request):
    if request.method == "POST":
        user_input = request.POST["user_input"]
        prompt = f"User: {user_input}\nAI:"
        response = generate_response(prompt)
        #print(response['message']['content'])
        print(response)
        return StreamingHttpResponse(response, content_type='text/plain')
    return render(request, "chat.html")

@csrf_exempt
def form_view(request):
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
        return render(request, "form-creation.html", {"chat_history": chat_history})

    # Render the initial page with an empty chat history
    return render(request, "form-creation.html", {"chat_history": []})