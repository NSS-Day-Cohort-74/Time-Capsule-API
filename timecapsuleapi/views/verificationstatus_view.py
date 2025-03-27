import logging
from django.http import HttpResponseServerError
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from timecapsuleapi.models import VerificationStatus

logger = logging.getLogger(__name__)


class VerificationStatusView(ViewSet):
    """Verification Status view set"""

    def retrieve(self, request, pk=None):
        """Handle GET requests for single verification status

        Returns:
            Response -- JSON serialized verification status
        """
        try:
            verification_status = VerificationStatus.objects.get(pk=pk)
            serializer = VerificationStatusSerializer(verification_status)
            return Response(serializer.data)
        except VerificationStatus.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            return Response({"reason": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        """Handle GET requests for all verification statuses

        Returns:
            Response -- JSON serialized array
        """
        try:
            verification_statuses = VerificationStatus.objects.all()
            serializer = VerificationStatusSerializer(verification_statuses, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as ex:
            return HttpResponseServerError(ex)


class VerificationStatusSerializer(serializers.ModelSerializer):
    """JSON serializer for verification statuses"""

    class Meta:
        model = VerificationStatus
        fields = (
            "id",
            "name",
        )