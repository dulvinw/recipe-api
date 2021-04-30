from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag

from recipe import serializers


class TagViewSet(viewsets.GenericViewSet,
                 mixins.ListModelMixin,
                 mixins.CreateModelMixin):
    """
    Manage tags in a database
    """

    permission_classes = (IsAuthenticated, )
    authentication_classes = (TokenAuthentication, )
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializers

    def get_queryset(self):
        """Return only the tags related to current auth user"""
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
