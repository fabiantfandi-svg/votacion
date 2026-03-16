from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from firebase_admin import auth
import firebase_admin
from votacion.firebase_config import initialize_firebase

# 1. Llamamos a la configuración para tener el "control remoto" de la base de datos
db = initialize_firebase()

class FirebaseAuthentication(BaseAuthentication):
    """
    Leer el token JWT del encabezado. lo va a validar con firebase y va a extraer el UID usuario
    """
    def authenticate(self, request):
        # 2. ¿Trae identificación? 
        # Buscamos en el mensaje que envía el usuario algo llamado 'Authorization'
        auth_header = request.META.get('HTTP_AUTHORIZATION') or request.headers.get('Authorization')
        
        if not auth_header:
            return None # Si no hay nada, el portero no hace nada (no lo identifica)

        # 3. Revisar el formato del carnet
        # El estándar pide que diga: "Bearer [el_codigo_largo]"
        # .split() pica ese texto en pedazos donde haya espacios
        partes = auth_header.split()

        # Si no tiene 2 partes o la primera no es 'bearer', el carnet no sirve
        if len(partes) != 2 or partes[0].lower() != 'bearer':
            return None
        
        # 4. Tomamos solo el código (el Token)
        token = partes[1]

        try:
            # 5. Llamada a la oficina central (Firebase)
            # Le preguntamos a Google: "¿Ustedes emitieron este código y sigue vigente?"
            decoded_token = auth.verify_id_token(token)
            
            # Si Google dice que sí, nos da el ID único (uid) y el correo (email)
            uid = decoded_token.get('uid')
            email = decoded_token.get('email')
            
            # 6. ¿Quién es este usuario en nuestra base de datos?
            # Vamos a Firestore, a la carpeta 'perfiles' y buscamos el documento con ese ID
            user_profile = db.collection('perfiles').document(uid).get()
            
            # Sacamos el 'rol'. Si no dice nada, por defecto es 'votante'
            rol = user_profile.to_dict().get('rol','votante') if user_profile.exists else 'votante'
            
            # 7. Crear el "Brazalete" de acceso (FirebaseUser)
            # Django necesita un objeto 'User' para trabajar. Como no usamos el de Django, 
            # fabricamos uno rápido aquí mismo con los datos que acabamos de conseguir.
            class FirebaseUser:
                def __init__(self, uid, rol, email):
                    self.uid = uid
                    self.rol = rol
                    self.email = email
                    self.is_authenticated = True

            # El portero termina entregando el usuario con su brazalete y los datos del token
            return (FirebaseUser(uid, rol, email), decoded_token)
        
        except Exception as e:
            # Si algo sale mal (token falso, expirado o error de conexión), se bloquea la entrada
            raise AuthenticationFailed(f"El token no es valido o esta expirado: {str(e)}")