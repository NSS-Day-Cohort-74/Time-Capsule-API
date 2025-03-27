import logging
from django.http import HttpResponseServerError
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from timecapsuleapi.models import DiscussionThread, TimeCapsule, UserProfile

logger = logging.getLogger(__name__)


class DiscussionThreadView(ViewSet):
    """Discussion Thread view set"""

    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized instance
        """
        discussion_thread = DiscussionThread()

        try:
            capsule = TimeCapsule.objects.get(pk=request.data["capsule"])
            discussion_thread.capsule = capsule
        except TimeCapsule.DoesNotExist:
            return Response(
                {"reason": "Invalid capsule id sent"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Set the created_by to the authenticated user
        authenticated_user_profile = UserProfile.objects.get(user=request.auth.user)
        discussion_thread.created_by = authenticated_user_profile

        discussion_thread.title = request.data["title"]

        try:
            discussion_thread.save()
            serializer = DiscussionThreadSerializer(discussion_thread, many=False)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as ex:
            return Response({"reason": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single discussion thread

        Returns:
            Response -- JSON serialized discussion thread
        """
        try:
            discussion_thread = DiscussionThread.objects.get(pk=pk)
            serializer = DiscussionThreadSerializer(discussion_thread)
            return Response(serializer.data)
        except DiscussionThread.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            return Response({"reason": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        """Handle PUT requests

        Returns:
            Response -- Empty body with 204 status code
        """
        try:
            discussion_thread = DiscussionThread.objects.get(pk=pk)

            # Check if the authenticated user is the creator of the thread
            authenticated_user_profile = UserProfile.objects.get(user=request.auth.user)
            if discussion_thread.created_by.id != authenticated_user_profile.id:
                return Response(
                    {"reason": "You are not authorized to update this thread"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # If capsule is provided, update it
            if "capsule" in request.data:
                try:
                    capsule = TimeCapsule.objects.get(pk=request.data["capsule"])
                    discussion_thread.capsule = capsule
                except TimeCapsule.DoesNotExist:
                    return Response(
                        {"reason": "Invalid capsule id sent"},
                        status=status.HTTP_404_NOT_FOUND,
                    )

            discussion_thread.title = request.data["title"]
            discussion_thread.save()
            return Response(None, status=status.HTTP_204_NO_CONTENT)

        except DiscussionThread.DoesNotExist:
            return Response(None, status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            logger.error(
                f"Error updating DiscussionThread with id {pk}: {str(ex)}",
                exc_info=True,
            )
            return HttpResponseServerError(ex)

    def destroy(self, request, pk=None):
        """Handle DELETE requests for a single discussion thread

        Returns:
            Response -- 204, 404, or 500 status code
        """
        try:
            discussion_thread = DiscussionThread.objects.get(pk=pk)

            # Check if the authenticated user is the creator of the thread
            authenticated_user_profile = UserProfile.objects.get(user=request.auth.user)
            if discussion_thread.created_by.id != authenticated_user_profile.id:
                return Response(
                    {"reason": "You are not authorized to delete this thread"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            discussion_thread.delete()
            return Response(None, status=status.HTTP_204_NO_CONTENT)

        except DiscussionThread.DoesNotExist as ex:
            return Response({"message": ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response(
                {"message": ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def list(self, request):
        """Handle GET requests for all discussion threads

        Returns:
            Response -- JSON serialized array
        """
        try:
            # Filter by capsule if provided
            capsule_id = request.query_params.get('capsule', None)

            # Filter by created_by if provided
            created_by_id = request.query_params.get('created_by', None)

            discussion_threads = DiscussionThread.objects.all().order_by('-created_at')

            if capsule_id:
                discussion_threads = discussion_threads.filter(capsule__id=capsule_id)

            if created_by_id:
                discussion_threads = discussion_threads.filter(created_by__id=created_by_id)

            serializer = DiscussionThreadSerializer(discussion_threads, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as ex:
            return HttpResponseServerError(ex)


class DiscussionThreadSerializer(serializers.ModelSerializer):
    """JSON serializer for discussion threads"""

    comment_count = serializers.SerializerMethodField()

    def get_comment_count(self, obj):
        return obj.comments.count()

    class Meta:
        model = DiscussionThread
        fields = (
            "id",
            "capsule",
            "title",
            "created_by",
            "created_at",
            "comment_count",
        )
        depth = 1