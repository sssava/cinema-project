from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from rest_framework import routers
from api.views import UserViewSet, AuthViewSet, MovieHallViewSet, SessionViewSet, SessionSeatDetail

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'auth', AuthViewSet)
router.register(r'halls', MovieHallViewSet)
router.register(r"sessions", SessionViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/sessions/<int:session_pk>/session-seats/', SessionSeatDetail.as_view(), name='sessionseat-detail'),
]
