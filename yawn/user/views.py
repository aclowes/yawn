from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from rest_framework import viewsets, status
from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .serializers import UserSerializer, LoginSerializer


class UserViewSet(viewsets.GenericViewSet,
                  viewsets.mixins.ListModelMixin,
                  viewsets.mixins.CreateModelMixin,
                  viewsets.mixins.RetrieveModelMixin,
                  viewsets.mixins.UpdateModelMixin):
    """
    User endpoint, GET(list, detail), PATCH to change
    """
    queryset = User.objects.all().order_by('id')

    serializer_class = UserSerializer

    @list_route(methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @list_route(methods=['patch'], permission_classes=[AllowAny])
    def login(self, request):
        credentials = LoginSerializer(data=request.data)
        credentials.is_valid(raise_exception=True)
        user = authenticate(request, **credentials.data)
        if not user:
            return Response({'detail': 'Login failed'}, status.HTTP_401_UNAUTHORIZED)

        login(request, user)
        return Response({'detail': 'Login succeeded'})

    @list_route(methods=['delete'])
    def logout(self, request):
        logout(request)
        return Response({'detail': 'Logout succeeded'})
