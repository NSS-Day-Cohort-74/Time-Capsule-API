from django.http import HttpResponseServerError
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from timecapsuleapi.models import TimeCapsule, UserProfile, CapsuleStatus, CapsuleType


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
            return Response({"reason": "Invalid capsule status id sent"}, status=status.HTTP_404_NOT_FOUND)

        try:
            capsule_type = CapsuleType.objects.get(pk=request.data["type"])
            capsule.type = capsule_type
        except CapsuleType.DoesNotExist:
            return Response({"reason": "Invalid capsule type id sent"}, status=status.HTTP_404_NOT_FOUND)


        capsule.title = request.data["title"]
        capsule.descriptions = request.data["description"]
        capsule.opening_date = request.data["openingDate"]
        capsule.location_x = request.data["x"]
        capsule.location_y = request.data["y"]

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
        # try:
        #     void = Void.objects.get(pk=pk)
        #     void.sample_name = request.data["name"]
        #     void.sample_description = request.data["description"]
        #     void.save()
        # except Void.DoesNotExist:
        #     return Response(None, status=status.HTTP_404_NOT_FOUND)

        # except Exception as ex:
        #     return HttpResponseServerError(ex)

        # return Response(None, status=status.HTTP_204_NO_CONTENT)
        pass

    def destroy(self, request, pk=None):
        """Handle DELETE requests for a single item

        Returns:
            Response -- 200, 404, or 500 status code
        """
        # try:
        #     void = Void.objects.get(pk=pk)
        #     void.delete()
        #     return Response(None, status=status.HTTP_204_NO_CONTENT)

        # except Void.DoesNotExist as ex:
        #     return Response({"message": ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        # except Exception as ex:
        #     return Response(
        #         {"message": ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        #     )
        pass

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
