import logging
from django.http import HttpResponseServerError
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from timecapsuleapi.models import StoryNode, TimeCapsuleContent

logger = logging.getLogger(__name__)


class StoryNodeView(ViewSet):
    """Story Node view set"""

    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized instance
        """
        story_node = StoryNode()

        try:
            capsule_content = TimeCapsuleContent.objects.get(pk=request.data["capsule_content"])
            story_node.capsule_content = capsule_content
        except TimeCapsuleContent.DoesNotExist:
            return Response(
                {"reason": "Invalid capsule content id sent"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # If parent_node is provided, set it
        if "parent_node" in request.data and request.data["parent_node"]:
            try:
                parent_node = StoryNode.objects.get(pk=request.data["parent_node"])
                story_node.parent_node = parent_node
            except StoryNode.DoesNotExist:
                return Response(
                    {"reason": "Invalid parent node id sent"},
                    status=status.HTTP_404_NOT_FOUND,
                )

        story_node.content = request.data["content"]

        try:
            story_node.save()
            serializer = StoryNodeSerializer(story_node, many=False)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as ex:
            return Response({"reason": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single story node

        Returns:
            Response -- JSON serialized story node
        """
        try:
            story_node = StoryNode.objects.get(pk=pk)
            serializer = StoryNodeSerializer(story_node)
            return Response(serializer.data)
        except StoryNode.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            return Response({"reason": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        """Handle PUT requests

        Returns:
            Response -- Empty body with 204 status code
        """
        try:
            story_node = StoryNode.objects.get(pk=pk)

            # If capsule_content is provided, update it
            if "capsule_content" in request.data:
                try:
                    capsule_content = TimeCapsuleContent.objects.get(pk=request.data["capsule_content"])
                    story_node.capsule_content = capsule_content
                except TimeCapsuleContent.DoesNotExist:
                    return Response(
                        {"reason": "Invalid capsule content id sent"},
                        status=status.HTTP_404_NOT_FOUND,
                    )

            # If parent_node is provided, update it
            if "parent_node" in request.data:
                if request.data["parent_node"]:
                    try:
                        parent_node = StoryNode.objects.get(pk=request.data["parent_node"])
                        story_node.parent_node = parent_node
                    except StoryNode.DoesNotExist:
                        return Response(
                            {"reason": "Invalid parent node id sent"},
                            status=status.HTTP_404_NOT_FOUND,
                        )
                else:
                    story_node.parent_node = None

            story_node.content = request.data["content"]
            story_node.save()
            return Response(None, status=status.HTTP_204_NO_CONTENT)

        except StoryNode.DoesNotExist:
            return Response(None, status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            logger.error(
                f"Error updating StoryNode with id {pk}: {str(ex)}",
                exc_info=True,
            )
            return HttpResponseServerError(ex)

    def destroy(self, request, pk=None):
        """Handle DELETE requests for a single story node

        Returns:
            Response -- 204, 404, or 500 status code
        """
        try:
            story_node = StoryNode.objects.get(pk=pk)
            story_node.delete()
            return Response(None, status=status.HTTP_204_NO_CONTENT)

        except StoryNode.DoesNotExist as ex:
            return Response({"message": ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response(
                {"message": ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def list(self, request):
        """Handle GET requests for all story nodes

        Returns:
            Response -- JSON serialized array
        """
        try:
            # Filter by capsule_content if provided
            capsule_content_id = request.query_params.get('capsule_content', None)

            # Filter by parent_node if provided
            parent_node_id = request.query_params.get('parent_node', None)

            # Get root nodes (nodes without parent) if specified
            root_nodes = request.query_params.get('root_nodes', None)

            story_nodes = StoryNode.objects.all()

            if capsule_content_id:
                story_nodes = story_nodes.filter(capsule_content__id=capsule_content_id)

            if parent_node_id:
                story_nodes = story_nodes.filter(parent_node__id=parent_node_id)

            if root_nodes and root_nodes.lower() == 'true':
                story_nodes = story_nodes.filter(parent_node=None)

            serializer = StoryNodeSerializer(story_nodes, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as ex:
            return HttpResponseServerError(ex)


class StoryNodeSerializer(serializers.ModelSerializer):
    """JSON serializer for story nodes"""

    class Meta:
        model = StoryNode
        fields = (
            "id",
            "capsule_content",
            "parent_node",
            "content",
            "created_at",
        )
        depth = 1