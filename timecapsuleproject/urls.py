from django.urls import include, path
from rest_framework import routers
from timecapsuleapi.views import (
    register_user, login_user, CapsuleView,
    CapsuleStatusView, CapsuleTypeView
)

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'capsules', CapsuleView, 'capsule')
router.register(r'capsulestatuses', CapsuleStatusView, 'capsulestatus')
router.register(r'capsuletypes', CapsuleTypeView, 'capsuletype')

urlpatterns = [
    path('', include(router.urls)),
    path('register', register_user), # Enables http://localhost:8000/register
    path('login', login_user), # Enables http://localhost:8000/login
]

