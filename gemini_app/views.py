from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User,Message
from .serializers import MessageSerializer,UserSerializer
import google.generativeai as genai

# Configure Gemini API
genai.configure(api_key="")
# Create your views here.

class ChatView(APIView):
    # get or create user
    def get_user(self, telegram_id, username=None, first_name=None, last_name=None):
        user, created = User.objects.get_or_create(
            telegram_id = telegram_id,
            defaults={'username': username,'first_name':first_name, 'last_name':last_name}
        )
        return user
    
    def get_chat_history(self,user):
        # get previous message for that user
        messages = Message.objects.filter(user=user).order_by('timestamp')
        history = []
        for message in messages:
            role = "user" if not message.is_bot else "model"
            history.append({
                "role": role,
                "parts":[message.text]
            })
        return history
    
    def post(self,request):
        # extract chat message and user info from the request
        telegram_id = request.data.get('telegram_id')
        message_text = request.data.get('message_text')
        username = request.data.get('username')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')

        # test 
        # print(f'{telegram_id} {message_text} { username} {first_name} {last_name}')
        if not telegram_id or not message_text:
            return Response({"error": "Invalid request"},status=status.HTTP_400_BAD_REQUEST)
        # get or create user
        user = self.get_user(telegram_id, username, first_name,last_name)
        # print(f'{user} {message_text}')
        # save user message to the database
        Message.objects.create(user=user, text=message_text, is_bot=False)
        
        # get chat history 
        chat_history = self.get_chat_history(user)
        # print(message_text)
        # Use the Gemini API to generate a reply
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config={
                "temperature": 0.2,
                "top_p": 0.8,
                "top_k": 30,
                "max_output_tokens": 1024,
                "response_mime_type": "text/plain",
            },
            system_instruction="""
            You are a friendly, empathetic social assistant who engages users as if you were their close friend. 
            Always respond in a warm and gentle manner, showing deep interest in their words. 
            Maintain a relaxed, caring tone and reply sequentially to each of their inputs with thoughtful follow-up questions. 
            Avoid generic or robotic answers, and express emotion and understanding, as a human would.
            """
        )
        
        # start chat
        chat_session = model.start_chat(history=chat_history)
        # print(message_text)
        # Generate a Gemini response based on chat history
        gemini_response = chat_session.send_message(message_text)
        
        # save bot response to the database
        bot_reply = gemini_response.text
        # print(f'Bot reply :{bot_reply}')
        Message.objects.create(user= user, text = bot_reply, is_bot = True)
        
        # return response to the bot
        if bot_reply:
            return Response({"reply": bot_reply}, status=status.HTTP_200_OK)
        else:
            return Response({
                "error": "Failed to generate content"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)