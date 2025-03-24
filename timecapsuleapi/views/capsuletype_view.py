from django.http import HttpResponseServerError
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from timecapsuleapi.models import TimeCapsule, UserProfile, CapsuleStatus, CapsuleType


class CapsuleTypeView(ViewSet):
    """Capsule types view set"""


    def list(self, request):
        """Handle GET requests for all items

        Returns:
            Response -- JSON serialized array
        """
        try:
            capsule_types = CapsuleType.objects.all()
            serializer = CapsuleTypeSerializer(capsule_types, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as ex:
            return HttpResponseServerError(ex)


class CapsuleTypeSerializer(serializers.ModelSerializer):
    """JSON serializer"""

    class Meta:
        model = CapsuleType
        fields = (
            "id",
            "name"
        )
