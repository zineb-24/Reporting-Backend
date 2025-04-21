from django.urls import path
from .views import UserDashboardView, UserDashboardStatsView

urlpatterns = [
    path('user-dashboard/', UserDashboardView.as_view(), name='user-dashboard'),
    path('user-dashboard/stats/', UserDashboardStatsView.as_view(), name='user-dashboard-stats'),
]