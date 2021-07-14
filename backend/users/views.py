from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.authtoken import views as auth_views
from rest_framework.compat import coreapi, coreschema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.schemas import ManualSchema
from rest_framework.views import APIView

from .models import Follow
from .serializers import FollowSerializer, MyAuthTokenSerializer

User = get_user_model()


class Logout(APIView):
    """Logout option"""

    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MyAuthToken(auth_views.ObtainAuthToken):
    serializer_class = MyAuthTokenSerializer
    if coreapi is not None and coreschema is not None:
        schema = ManualSchema(
            fields=[
                coreapi.Field(
                    name="email",
                    required=True,
                    location='form',
                    schema=coreschema.String(
                        title="Email",
                        description="Valid email for authentication",
                    ),
                ),
                coreapi.Field(
                    name="password",
                    required=True,
                    location='form',
                    schema=coreschema.String(
                        title="Password",
                        description="Valid password for authentication",
                    ),
                ),
            ],
            encoding="application/json",
        )


class ListFollowViewSet(generics.ListAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, ]
    serializer_class = FollowSerializer

    def get_serializer_context(self):
        context = super(ListFollowViewSet, self).get_serializer_context()
        context.update({'request': self.request})
        return context

    def get_queryset(self):
        user = self.request.user
        follows = user.follower.all()
        return [record.author for record in follows]


class FollowViewSet(APIView):
    """
    APIView with post and delete options.
    Used to create and delete Follow objects.
    """
    permission_classes = [IsAuthenticated, ]

    def post(self, request, author_id):
        user = self.request.user
        author = get_object_or_404(User, id=author_id)
        if user == author:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        Follow.objects.get_or_create(user=user, author=author)
        serializer = FollowSerializer(author, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, author_id):
        user = self.request.user
        author = get_object_or_404(User, id=author_id)
        obj = get_object_or_404(Follow, user=user, author=author)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


logout = Logout.as_view()
obtain_auth_token = MyAuthToken.as_view()
