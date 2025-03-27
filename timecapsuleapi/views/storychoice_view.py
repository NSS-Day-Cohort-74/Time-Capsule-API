import logging
from django.http import HttpResponseServerError
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from timecapsuleapi.models import StoryChoice, StoryNode

logger = logging.getLogger(__name__)


class StoryChoiceView(ViewSet):
    """Story Choice view set"""

    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized instance
        """
        story_choice = StoryChoice()

        try:
            node = StoryNode.objects.get(pk=request.data["node"])
            story_choice.node = node
        except StoryNode.DoesNotExist:
            return Response(
                {"reason": "Invalid node id sent"},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            next_node = StoryNode.objects.get(pk=request.data["next_node"])
            story_choice.next_node = next_node
        except StoryNode.DoesNotExist:
            return Response(
                {"reason": "Invalid next_node id sent"},
                status=status.HTTP_404_NOT_FOUND,
            )

        story_choice.choice_text = request.data["choice_text"]

        try:
            story_choice.save()
            serializer = StoryChoiceSerializer(story_choice, many=False)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as ex:
            return Response({"reason": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single story choice

        Returns:
            Response -- JSON serialized story choice
        """
        try:
            story_choice = StoryChoice.objects.get(pk=pk)
            serializer = StoryChoiceSerializer(story_choice)
            return Response(serializer.data)
        except StoryChoice.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            return Response({"reason": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        """Handle PUT requests

        Returns:
            Response -- Empty body with 204 status code
        """
        try:
            story_choice = StoryChoice.objects.get(pk=pk)

            # If node is provided, update it
            if "node" in request.data:
                try:
                    node = StoryNode.objects.get(pk=request.data["node"])
                    story_choice.node = node
                except StoryNode.DoesNotExist:
                    return Response(
                        {"reason": "Invalid node id sent"},
                        status=status.HTTP_404_NOT_FOUND,
                    )

            # If next_node is provided, update it
            if "next_node" in request.data:
                try:
                    next_node = StoryNode.objects.get(pk=request.data["next_node"])
                    story_choice.next_node = next_node
                except StoryNode.DoesNotExist:
                    return Response(
                        {"reason": "Invalid next_node id sent"},
                        status=status.HTTP_404_NOT_FOUND,
                    )

            story_choice.choice_text = request.data["choice_text"]
            story_choice.save()
            return Response(None, status=status.HTTP_204_NO_CONTENT)

        except StoryChoice.DoesNotExist:
            return Response(None, status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            logger.error(
                f"Error updating StoryChoice with id {pk}: {str(ex)}",
                exc_info=True,
            )
            return HttpResponseServerError(ex)

    def destroy(self, request, pk=None):
        """Handle DELETE requests for a single story choice

        Returns:
            Response -- 204, 404, or 500 status code
        """
        try:
            story_choice = StoryChoice.objects.get(pk=pk)
            story_choice.delete()
            return Response(None, status=status.HTTP_204_NO_CONTENT)

        except StoryChoice.DoesNotExist as ex:
            return Response({"message": ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response(
                {"message": ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def list(self, request):
        """Handle GET requests for all story choices

        Returns:
            Response -- JSON serialized array
        """
        try:
            # Filter by node if provided
            node_id = request.query_params.get('node', None)

            # Filter by next_node if provided
            next_node_id = request.query_params.get('next_node', None)

            story_choices = StoryChoice.objects.all()

            if node_id:
                story_choices = story_choices.filter(node__id=node_id)

            if next_node_id:
                story_choices = story_choices.filter(next_node__id=next_node_id)

            serializer = StoryChoiceSerializer(story_choices, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as ex:
            return HttpResponseServerError(ex)


class StoryChoiceSerializer(serializers.ModelSerializer):
    """JSON serializer for story choices"""

    class Meta:
        model = StoryChoice
        fields = (
            "id",
            "node",
            "choice_text",
            "next_node",
            "created_at",
        )
        depth = 1