import logging
from django.http import HttpResponseServerError
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from timecapsuleapi.models import TimeCapsule, UserProfile, CapsuleStatus, CapsuleType

logger = logging.getLogger(__name__)


class CapsuleView(ViewSet):
    """Void view set"""

    def create(self, request):
        """Handle POST operationsÇÇ‰

        Returns:
            Response -- JSON serialized instance
        """
        capsule = TimeCapsule()
        authenticated_user_profile = UserProfile.objects.get(user=request.auth.user)
        capsule.creator = authenticated_user_profile

        try:
            capsule_status = CapsuleStatus.objects.get(pk=request.data["status"])
            capsule.status = capsule_status
        except CapsuleStatus.DoesNotExist:
            return Response(
                {"reason": "Invalid capsule status id sent"},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            capsule_type = CapsuleType.objects.get(pk=request.data["type"])
            capsule.type = capsule_type
        except CapsuleType.DoesNotExist:
            return Response(
                {"reason": "Invalid capsule type id sent"},
                status=status.HTTP_404_NOT_FOUND,
            )

        capsule.title = request.data["title"]
        capsule.descriptions = request.data["descriptions"]
        capsule.opening_date = request.data["opening_date"]
        capsule.location_x = request.data["location_x"]
        capsule.location_y = request.data["location_y"]

        try:
            capsule.save()
            serializer = CapsuleSerializer(capsule, many=False)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as ex:
            return Response({"reason": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single item

        Returns:
            Response -- JSON serialized instance
        """
        # try:
        #     void = Void.objects.get(pk=pk)
        #     serializer = VoidSerializer(void)
        #     return Response(serializer.data)
        # except Exception as ex:
        #     return Response({"reason": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)
        pass

    def update(self, request, pk=None):
        """Handle PUT requests

        Returns:
            Response -- Empty body with 204 status code
        """
        try:
            timecapsule = TimeCapsule.objects.get(pk=pk)

            try:
                capsule_status = CapsuleStatus.objects.get(pk=request.data["status"])
                timecapsule.status = capsule_status
            except CapsuleStatus.DoesNotExist:
                return Response(
                    {"reason": "Invalid capsule status id sent"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            try:
                capsule_type = CapsuleType.objects.get(pk=request.data["type"])
                timecapsule.type = capsule_type
            except CapsuleType.DoesNotExist:
                return Response(
                    {"reason": "Invalid capsule type id sent"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            timecapsule.title = request.data["title"]
            timecapsule.descriptions = request.data["descriptions"]
            timecapsule.opening_date = request.data["opening_date"]
            timecapsule.location_x = request.data["location_x"]
            timecapsule.location_y = request.data["location_y"]

            timecapsule.save()
        except TimeCapsule.DoesNotExist:
            return Response(None, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            logger.error(
                f"Error updating TimeCapsule with id {pk}: {str(ex)}",
                exc_info=True,  # This includes the full traceback
            )
            return HttpResponseServerError(ex)

        return Response(None, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        """Handle DELETE requests for a single item

        Returns:
            Response -- 200, 404, or 500 status code
        """
        try:
            capsule = TimeCapsule.objects.get(pk=pk)
            capsule.delete()
            return Response(None, status=status.HTTP_204_NO_CONTENT)

        except TimeCapsule.DoesNotExist as ex:
            return Response({"message": ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response(
                {"message": ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def list(self, request):
        """Handle GET requests for all items

        Returns:
            Response -- JSON serialized array
        """
        try:
            capsules = TimeCapsule.objects.all()
            serializer = CapsuleSerializer(capsules, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as ex:
            return HttpResponseServerError(ex)


class CapsuleSerializer(serializers.ModelSerializer):
    """JSON serializer"""

    opening_date = serializers.SerializerMethodField()

    def get_opening_date(self, obj):
        return obj.opening_date.strftime("%Y-%m-%d")

    class Meta:
        model = TimeCapsule
        fields = (
            "id",
            "status",
            "type",
            "title",
            "descriptions",
            "opening_date",
            "location_x",
            "location_y",
        )
