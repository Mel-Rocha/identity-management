from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from celery.result import AsyncResult

from apps.users.views import IsStaffOrAdmin


class TaskResultView(APIView):
    permission_classes = [IsAuthenticated, IsStaffOrAdmin]

    def get(self, request, task_id, *args, **kwargs):
        try:
            task_result = AsyncResult(task_id)

            return Response({
                "task_id": task_id,
                "status": task_result.status,
                "result": task_result.result
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "error": "Erro ao buscar o resultado da tarefa: " + str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
