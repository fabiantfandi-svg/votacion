import cloudinary.uploader
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from .authentication import FirebaseAuthentication 
from votacion.firebase_config import initialize_firebase
from drf_spectacular.utils import extend_schema # Añadido

db = initialize_firebase()

class PerfilImagenAPIView(APIView):
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    @extend_schema(
        summary="Actualizar foto de perfil",
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'imagen': {'type': 'string', 'format': 'binary'}
                }
            }
        }
    )
    def post(self, request):
        file_to_upload = request.FILES.get('imagen')
        if not file_to_upload:
            return Response({"error": "No se envió imagen"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            uid = request.user.uid
            upload_result = cloudinary.uploader.upload(
                file_to_upload,
                folder=f"votaciones/perfiles/{uid}/",
                public_id="foto_perfil",
                overwrite=True
            )
            url_imagen = upload_result.get('secure_url')
            db.collection('perfiles').document(uid).update({'foto_url': url_imagen})
            return Response({"mensaje": "Foto actualizada", "url": url_imagen}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)