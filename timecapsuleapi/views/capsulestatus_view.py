from django.http import HttpResponseServerError
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from timecapsuleapi.models import CapsuleStatus


class CapsuleStatusView(ViewSet):
    """Capsule statuss view set"""


    def list(self, request):
        """Handle GET requests for all items

        Returns:
            Response -- JSON serialized array
        """
        try:
            capsule_statuss = CapsuleStatus.objects.all()
            serializer = CapsuleStatusSerializer(capsule_statuss, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as ex:
            return HttpResponseServerError(ex)


class CapsuleStatusSerializer(serializers.ModelSerializer):
    """JSON serializer"""

    class Meta:
        model = CapsuleStatus
        fields = (
            "id",
            "name"
        )
