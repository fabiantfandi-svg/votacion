from rest_framework import serializers

class VotoSerializer(serializers.Serializer):
    """
    Validar los datos del voto antes de guardarlos en Firestore
    """
    candidato_id = serializers.CharField(max_length=50)
    mesa_id = serializers.CharField(max_length=20)
    comentario = serializers.CharField(required=False, allow_blank=True)

    # Regla de calidad: El candidato debe tener un código válido
    def validate_candidato_id(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("El ID del candidato es demasiado corto, revisa el código.")
        return value

    # Regla de calidad: La mesa debe seguir un formato específico (ejemplo: MESA-01)
    def validate_mesa_id(self, value):
        if "MESA" not in value.upper():
            raise serializers.ValidationError("El formato de la mesa debe incluir la palabra 'MESA'")
        return value