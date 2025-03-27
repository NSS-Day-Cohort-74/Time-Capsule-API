import logging
from django.http import HttpResponseServerError
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from timecapsuleapi.models import DiscussionComment, DiscussionThread, UserProfile

logger = logging.getLogger(__name__)


class DiscussionCommentView(ViewSet):
    """Discussion Comment view set"""

    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized instance
        """
        discussion_comment = DiscussionComment()

        try:
            thread = DiscussionThread.objects.get(pk=request.data["thread"])
            discussion_comment.thread = thread
        except DiscussionThread.DoesNotExist:
            return Response(
                {"reason": "Invalid thread id sent"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Set the author to the authenticated user
        authenticated_user_profile = UserProfile.objects.get(user=request.auth.user)
        discussion_comment.author = authenticated_user_profile

        discussion_comment.content = request.data["content"]

        try:
            discussion_comment.save()
            serializer = DiscussionCommentSerializer(discussion_comment, many=False)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as ex:
            return Response({"reason": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single discussion comment

        Returns:
            Response -- JSON serialized discussion comment
        """
        try:
            discussion_comment = DiscussionComment.objects.get(pk=pk)
            serializer = DiscussionCommentSerializer(discussion_comment)
            return Response(serializer.data)
        except DiscussionComment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            return Response({"reason": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        """Handle PUT requests

        Returns:
            Response -- Empty body with 204 status code
        """
        try:
            discussion_comment = DiscussionComment.objects.get(pk=pk)

            # Check if the authenticated user is the author of the comment
            authenticated_user_profile = UserProfile.objects.get(user=request.auth.user)
            if discussion_comment.author.id != authenticated_user_profile.id:
                return Response(
                    {"reason": "You are not authorized to update this comment"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # If thread is provided, update it
            if "thread" in request.data:
                try:
                    thread = DiscussionThread.objects.get(pk=request.data["thread"])
                    discussion_comment.thread = thread
                except DiscussionThread.DoesNotExist:
                    return Response(
                        {"reason": "Invalid thread id sent"},
                        status=status.HTTP_404_NOT_FOUND,
                    )

            discussion_comment.content = request.data["content"]
            discussion_comment.save()
            return Response(None, status=status.HTTP_204_NO_CONTENT)

        except DiscussionComment.DoesNotExist:
            return Response(None, status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            logger.error(
                f"Error updating DiscussionComment with id {pk}: {str(ex)}",
                exc_info=True,
            )
            return HttpResponseServerError(ex)

    def destroy(self, request, pk=None):
        """Handle DELETE requests for a single discussion comment

        Returns:
            Response -- 204, 404, or 500 status code
        """
        try:
            discussion_comment = DiscussionComment.objects.get(pk=pk)

            # Check if the authenticated user is the author of the comment
            authenticated_user_profile = UserProfile.objects.get(user=request.auth.user)
            if discussion_comment.author.id != authenticated_user_profile.id:
                return Response(
                    {"reason": "You are not authorized to delete this comment"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            discussion_comment.delete()
            return Response(None, status=status.HTTP_204_NO_CONTENT)

        except DiscussionComment.DoesNotExist as ex:
            return Response({"message": ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response(
                {"message": ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def list(self, request):
        """Handle GET requests for all discussion comments

        Returns:
            Response -- JSON serialized array
        """
        try:
            # Filter by thread if provided
            thread_id = request.query_params.get('thread', None)

            # Filter by author if provided
            author_id = request.query_params.get('author', None)

            discussion_comments = DiscussionComment.objects.all().order_by('created_at')

            if thread_id:
                discussion_comments = discussion_comments.filter(thread__id=thread_id)

            if author_id:
                discussion_comments = discussion_comments.filter(author__id=author_id)

            serializer = DiscussionCommentSerializer(discussion_comments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as ex:
            return HttpResponseServerError(ex)


class DiscussionCommentSerializer(serializers.ModelSerializer):
    """JSON serializer for discussion comments"""

    class Meta:
        model = DiscussionComment
        fields = (
            "id",
            "thread",
            "content",
            "author",
            "created_at",
        )
        depth = 1