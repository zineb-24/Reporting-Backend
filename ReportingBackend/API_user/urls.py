from django.urls import path
from .views import UserDashboardView, UserDashboardStatsView, UserDashboardRevenueView, UserDashboardDistributionView, UserDashboardReportsView

urlpatterns = [
    path('user-dashboard/', UserDashboardView.as_view(), name='user-dashboard'),
    path('user-dashboard/stats/', UserDashboardStatsView.as_view(), name='user-dashboard-stats'),
    path('user-dashboard/revenue/', UserDashboardRevenueView.as_view(), name='user-dashboard-revenue'),
    path('user-dashboard/distribution/', UserDashboardDistributionView.as_view(), name='user-dashboard-distribution'),
    path('user-dashboard/reports/', UserDashboardReportsView.as_view(), name='user-dashboard-reports'),
]