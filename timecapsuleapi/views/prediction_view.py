import logging
from django.http import HttpResponseServerError
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from timecapsuleapi.models import Prediction, TimeCapsuleContent, VerificationStatus, UserProfile

logger = logging.getLogger(__name__)


class PredictionView(ViewSet):
    """Prediction view set"""

    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized instance
        """
        prediction = Prediction()

        try:
            capsule_content = TimeCapsuleContent.objects.get(pk=request.data["capsule_content"])
            prediction.capsule_content = capsule_content
        except TimeCapsuleContent.DoesNotExist:
            return Response(
                {"reason": "Invalid capsule content id sent"},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            # Default to 'pending' verification status
            verification_status = VerificationStatus.objects.get(name="pending")
            prediction.verification_status = verification_status
        except VerificationStatus.DoesNotExist:
            return Response(
                {"reason": "Verification status 'pending' not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        prediction.prediction_text = request.data["prediction_text"]

        if "category" in request.data:
            prediction.category = request.data["category"]

        try:
            prediction.save()
            serializer = PredictionSerializer(prediction, many=False)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as ex:
            return Response({"reason": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single prediction

        Returns:
            Response -- JSON serialized prediction
        """
        try:
            prediction = Prediction.objects.get(pk=pk)
            serializer = PredictionSerializer(prediction)
            return Response(serializer.data)
        except Prediction.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            return Response({"reason": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        """Handle PUT requests

        Returns:
            Response -- Empty body with 204 status code
        """
        try:
            prediction = Prediction.objects.get(pk=pk)

            # If capsule_content is provided, update it
            if "capsule_content" in request.data:
                try:
                    capsule_content = TimeCapsuleContent.objects.get(pk=request.data["capsule_content"])
                    prediction.capsule_content = capsule_content
                except TimeCapsuleContent.DoesNotExist:
                    return Response(
                        {"reason": "Invalid capsule content id sent"},
                        status=status.HTTP_404_NOT_FOUND,
                    )

            prediction.prediction_text = request.data["prediction_text"]

            if "category" in request.data:
                prediction.category = request.data["category"]

            prediction.save()
            return Response(None, status=status.HTTP_204_NO_CONTENT)

        except Prediction.DoesNotExist:
            return Response(None, status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            logger.error(
                f"Error updating Prediction with id {pk}: {str(ex)}",
                exc_info=True,
            )
            return HttpResponseServerError(ex)

    def destroy(self, request, pk=None):
        """Handle DELETE requests for a single prediction

        Returns:
            Response -- 204, 404, or 500 status code
        """
        try:
            prediction = Prediction.objects.get(pk=pk)
            prediction.delete()
            return Response(None, status=status.HTTP_204_NO_CONTENT)

        except Prediction.DoesNotExist as ex:
            return Response({"message": ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response(
                {"message": ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def list(self, request):
        """Handle GET requests for all predictions

        Returns:
            Response -- JSON serialized array
        """
        try:
            # Filter by capsule_content if provided
            capsule_content_id = request.query_params.get('capsule_content', None)

            # Filter by verification_status if provided
            verification_status_id = request.query_params.get('verification_status', None)

            # Filter by category if provided
            category = request.query_params.get('category', None)

            predictions = Prediction.objects.all()

            if capsule_content_id:
                predictions = predictions.filter(capsule_content__id=capsule_content_id)

            if verification_status_id:
                predictions = predictions.filter(verification_status__id=verification_status_id)

            if category:
                predictions = predictions.filter(category=category)

            serializer = PredictionSerializer(predictions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as ex:
            return HttpResponseServerError(ex)

    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Handle verification of a prediction

        Returns:
            Response -- Empty body with 204 status code
        """
        try:
            prediction = Prediction.objects.get(pk=pk)

            # Get the verification status
            try:
                verification_status_id = request.data["verification_status"]
                verification_status = VerificationStatus.objects.get(pk=verification_status_id)
                prediction.verification_status = verification_status
            except VerificationStatus.DoesNotExist:
                return Response(
                    {"reason": "Invalid verification status id sent"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Set the verification user to the authenticated user
            authenticated_user_profile = UserProfile.objects.get(user=request.auth.user)
            prediction.verification_user = authenticated_user_profile

            # Set the verification date to now (handled by model save)
            from django.utils import timezone
            prediction.verification_date = timezone.now()

            prediction.save()
            return Response(None, status=status.HTTP_204_NO_CONTENT)

        except Prediction.DoesNotExist:
            return Response(None, status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            logger.error(
                f"Error verifying Prediction with id {pk}: {str(ex)}",
                exc_info=True,
            )
            return HttpResponseServerError(ex)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get statistics about predictions

        Returns:
            Response -- JSON with statistics
        """
        try:
            # Count predictions by verification status
            verification_stats = {}
            verification_statuses = VerificationStatus.objects.all()

            for vs in verification_statuses:
                count = Prediction.objects.filter(verification_status=vs).count()
                verification_stats[vs.name] = count

            # Count predictions by category
            category_stats = {}
            categories = Prediction.objects.values_list('category', flat=True).distinct()

            for category in categories:
                if category:  # Skip None values
                    count = Prediction.objects.filter(category=category).count()
                    category_stats[category] = count

            # Overall accuracy (verified / total verified+disproved)
            try:
                verified = Prediction.objects.filter(verification_status__name="verified").count()
                disproved = Prediction.objects.filter(verification_status__name="disproved").count()
                total = verified + disproved

                accuracy = 0
                if total > 0:
                    accuracy = (verified / total) * 100

                accuracy_stats = {
                    "verified": verified,
                    "disproved": disproved,
                    "total_verified": total,
                    "accuracy_percentage": accuracy
                }
            except:
                accuracy_stats = {
                    "verified": 0,
                    "disproved": 0,
                    "total_verified": 0,
                    "accuracy_percentage": 0
                }

            statistics = {
                "verification_stats": verification_stats,
                "category_stats": category_stats,
                "accuracy_stats": accuracy_stats
            }

            return Response(statistics, status=status.HTTP_200_OK)
        except Exception as ex:
            logger.error(
                f"Error getting prediction statistics: {str(ex)}",
                exc_info=True,
            )
            return HttpResponseServerError(ex)


class PredictionSerializer(serializers.ModelSerializer):
    """JSON serializer for predictions"""

    class Meta:
        model = Prediction
        fields = (
            "id",
            "capsule_content",
            "prediction_text",
            "category",
            "verification_status",
            "verification_date",
            "verification_user",
            "created_at",
        )
        depth = 1