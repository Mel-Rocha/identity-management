from django.urls import path
from apps.core.views import TaskResultView

urlpatterns = [
    path('task-result/<str:task_id>/', TaskResultView.as_view(), name='task_result'),
]
