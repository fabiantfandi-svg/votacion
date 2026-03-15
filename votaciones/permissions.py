from rest_framework import permissions

class IsAdminVotacion(permissions.BasePermission):
    """
    Permitir el acceso unicamente a los usuarios con rol 'admin'
    (Quienes pueden crear candidatos o ver resultados)
    """
    def has_permission(self, request, view):
        # Verificamos que el usuario exista y que su brazalete diga 'admin'
        return bool(request.user and request.user.rol == 'admin')

class IsVotante(permissions.BasePermission):
    """
    Permitir el acceso a los usuarios con rol 'votante'
    (Quienes pueden enviar su voto)
    """
    def has_permission(self, request, view):
        # Verificamos que el usuario exista y que su brazalete diga 'votante'
        return bool(request.user and request.user.rol == 'votante')