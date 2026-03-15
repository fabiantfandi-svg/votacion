from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import VotoSerializer
from votacion.firebase_config import initialize_firebase
from firebase_admin import firestore
from rest_framework.permissions import IsAuthenticated
from .authentication import FirebaseAuthentication
from .permissions import IsAdminVotacion

db = initialize_firebase()

class VotacionAPIView(APIView):
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Listar votos (Administrador ve todos, Votante ve solo los suyos)
        """
        uid_usuario = request.user.uid
        rol_usuario = request.user.rol

        try:
            query = db.collection('api_votos')

            # Si no eres admin, solo ves tus propios votos
            if rol_usuario != 'admin':
                query = query.where('usuario_id', '==', uid_usuario)

            docs = query.stream()
            votos = [{'id': doc.id, **doc.to_dict()} for doc in docs]

            return Response({"rol": rol_usuario, "datos": votos}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"Error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        """
        Emitir un nuevo voto
        """
        serializer = VotoSerializer(data=request.data)

        if serializer.is_valid():
            datos_validados = serializer.validated_data
            datos_validados['usuario_id'] = request.user.uid
            datos_validados['fecha_voto'] = firestore.SERVER_TIMESTAMP

            try:
                # Guardar el voto en la colección 'api_votos'
                nuevo_voto = db.collection('api_votos').add(datos_validados)
                return Response({"mensaje": "Voto registrado exitosamente", "id": nuevo_voto[1].id}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"Error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)