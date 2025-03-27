import logging
from django.http import HttpResponseServerError
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from timecapsuleapi.models import TimeCapsule, UserProfile, CapsuleStatus

logger = logging.getLogger(__name__)


class UserTimelineView(ViewSet):
    """User Timeline view set"""

    def list(self, request):
        """Handle GET requests for user timeline

        Returns:
            Response -- JSON serialized array
        """
        try:
            # Get the authenticated user
            authenticated_user_profile = UserProfile.objects.get(user=request.auth.user)

            # Get all capsules created by the user
            created_capsules = TimeCapsule.objects.filter(creator=authenticated_user_profile).order_by('-created_at')

            # Get all capsules the user has access to (but didn't create)
            # This would require additional logic based on your access control model
            # For example, if you have a model that tracks which users have access to which capsules
            # accessible_capsules = TimeCapsule.objects.filter(access_controls__user=authenticated_user_profile).exclude(creator=authenticated_user_profile)

            # For now, we'll just return the created capsules
            serializer = TimelineCapsuleSerializer(created_capsules, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as ex:
            return HttpResponseServerError(ex)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get statistics about user's capsules

        Returns:
            Response -- JSON with statistics
        """
        try:
            # Get the authenticated user
            authenticated_user_profile = UserProfile.objects.get(user=request.auth.user)

            # Count capsules by status
            status_stats = {}
            capsule_statuses = CapsuleStatus.objects.all()

            for cs in capsule_statuses:
                count = TimeCapsule.objects.filter(creator=authenticated_user_profile, status=cs).count()
                status_stats[cs.name] = count

            # Count total capsules created
            total_created = TimeCapsule.objects.filter(creator=authenticated_user_profile).count()

            # Count total discussions started
            total_discussions = authenticated_user_profile.discussion_threads.count()

            # Count total comments made
            total_comments = authenticated_user_profile.discussion_comments.count()

            # Count total predictions verified
            total_verified = authenticated_user_profile.verified_predictions.count()

            statistics = {
                "status_stats": status_stats,
                "total_created": total_created,
                "total_discussions": total_discussions,
                "total_comments": total_comments,
                "total_verified": total_verified,
                "achievements": self._calculate_achievements(authenticated_user_profile)
            }

            return Response(statistics, status=status.HTTP_200_OK)
        except Exception as ex:
            logger.error(
                f"Error getting user statistics: {str(ex)}",
                exc_info=True,
            )
            return HttpResponseServerError(ex)

    @action(detail=False, methods=['get'])
    def discovery_history(self, request):
        """Get history of capsules discovered by the user

        Returns:
            Response -- JSON with discovery history
        """
        try:
            # Get the authenticated user
            authenticated_user_profile = UserProfile.objects.get(user=request.auth.user)

            # This would require a model that tracks which capsules a user has discovered
            # For now, we'll return an empty list
            return Response([], status=status.HTTP_200_OK)
        except Exception as ex:
            logger.error(
                f"Error getting discovery history: {str(ex)}",
                exc_info=True,
            )
            return HttpResponseServerError(ex)

    def _calculate_achievements(self, user_profile):
        """Calculate achievements for a user

        Args:
            user_profile: The user profile to calculate achievements for

        Returns:
            List of achievements
        """
        achievements = []

        # Count total capsules created
        total_created = TimeCapsule.objects.filter(creator=user_profile).count()

        # Achievement for creating capsules
        if total_created >= 1:
            achievements.append({
                "name": "Time Capsule Creator",
                "description": "Created your first time capsule",
                "date_earned": TimeCapsule.objects.filter(creator=user_profile).order_by('created_at').first().created_at
            })

        if total_created >= 5:
            achievements.append({
                "name": "Time Capsule Enthusiast",
                "description": "Created 5 time capsules",
                "date_earned": TimeCapsule.objects.filter(creator=user_profile).order_by('created_at')[4].created_at
            })

        if total_created >= 10:
            achievements.append({
                "name": "Time Capsule Master",
                "description": "Created 10 time capsules",
                "date_earned": TimeCapsule.objects.filter(creator=user_profile).order_by('created_at')[9].created_at
            })

        # Achievement for starting discussions
        total_discussions = user_profile.discussion_threads.count()
        if total_discussions >= 1:
            achievements.append({
                "name": "Discussion Starter",
                "description": "Started your first discussion",
                "date_earned": user_profile.discussion_threads.order_by('created_at').first().created_at
            })

        # Achievement for verifying predictions
        total_verified = user_profile.verified_predictions.count()
        if total_verified >= 1:
            achievements.append({
                "name": "Prediction Verifier",
                "description": "Verified your first prediction",
                "date_earned": user_profile.verified_predictions.order_by('verification_date').first().verification_date
            })

        return achievements


class TimelineCapsuleSerializer(serializers.ModelSerializer):
    """JSON serializer for timeline capsules"""

    opening_date = serializers.SerializerMethodField()
    discussion_count = serializers.SerializerMethodField()

    def get_opening_date(self, obj):
        return obj.opening_date.strftime("%Y-%m-%d")

    def get_discussion_count(self, obj):
        return obj.discussion_threads.count()

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
            "created_at",
            "discussion_count",
        )
        depth = 1