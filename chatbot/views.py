from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from .models import Chat
from .serializers import ChatSerializer
import google.generativeai as genai
from django.conf import settings

GEMINI_API_KEY = settings.GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)
system_instruction = (
            "You are a fitness assistant. Only answer questions related to fitness, "
            "workouts, nutrition, and health. If a question is unrelated to fitness, "
            "respond that you can only discuss fitness topics."
        )
model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=system_instruction)



class ChatbotView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        print(user)
        data = request.data
        response = model.generate_content(data['message'])

        chat = Chat.objects.create(user=user, message=data['message'], response=response.text)
        serializer = ChatSerializer(chat)
        return Response(serializer.data)
    
    def get(self, request):
        user = request.user
        chats = Chat.objects.filter(user=user)
        serializer = ChatSerializer(chats, many=True)
        return Response(serializer.data)