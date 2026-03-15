import os
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from firebase_admin import auth, firestore
from votacion.firebase_config import initialize_firebase 

db = initialize_firebase()

class RegistroAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({"error": "Faltan credenciales"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = auth.create_user(email=email, password=password)
            db.collection('perfiles').document(user.uid).set({
                'email': email,
                'rol': 'votante', 
                'fecha_registro': firestore.SERVER_TIMESTAMP
            })
            return Response({"mensaje": "Usuario registrado", "uid": user.uid}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class LoginApiView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        api_key = os.getenv('FIREBASE_WEB_API_KEY')

        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
        payload = {"email": email, "password": password, "returnSecureToken": True}

        try:
            response = requests.post(url, json=payload)
            data = response.json()
            if response.status_code == 200:
                return Response({"token": data['idToken'], "uid": data['localId']}, status=status.HTTP_200_OK)
            return Response({"error": data.get('error', {}).get('message')}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"error": "Fallo técnico"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)