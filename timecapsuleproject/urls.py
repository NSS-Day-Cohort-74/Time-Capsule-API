from django.urls import include, path
from rest_framework import routers
from timecapsuleapi.views import (
    register_user, login_user, CapsuleView,
    CapsuleStatusView, CapsuleTypeView,
    StoryNodeView, StoryChoiceView,
    PredictionView, VerificationStatusView,
    DiscussionThreadView, DiscussionCommentView,
    UserTimelineView
)

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'capsules', CapsuleView, 'capsule')
router.register(r'capsulestatuses', CapsuleStatusView, 'capsulestatus')
router.register(r'capsuletypes', CapsuleTypeView, 'capsuletype')
router.register(r'storynodes', StoryNodeView, 'storynode')
router.register(r'storychoices', StoryChoiceView, 'storychoice')
router.register(r'predictions', PredictionView, 'prediction')
router.register(r'verificationstatuses', VerificationStatusView, 'verificationstatus')
router.register(r'discussionthreads', DiscussionThreadView, 'discussionthread')
router.register(r'discussioncomments', DiscussionCommentView, 'discussioncomment')
router.register(r'usertimeline', UserTimelineView, 'usertimeline')

urlpatterns = [
    path('', include(router.urls)),
    path('register', register_user), # Enables http://localhost:8000/register
    path('login', login_user), # Enables http://localhost:8000/login
]
