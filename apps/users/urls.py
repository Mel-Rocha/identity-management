from django.urls import path

from apps.users.views import (LoginView, ListUsers, SignUpView,
                              RecoverPassword, UpdateUser, InactivateUser, ActivateUser, LogoutView, MeView)

urlpatterns = [
    path(
        'login-service/',
        LoginView.as_view(),
        name='login'),
    path(
        'signup-service/',
        SignUpView.as_view(),
        name='signup'),
    path(
        'users-list-service/',
        ListUsers.as_view(),
        name='users-list'),
    path(
        'user-update-service/',
        UpdateUser.as_view(),
        name='user-update'),
    path(
        'recover_password-service/',
        RecoverPassword.as_view(),
        name='recover_password'),
    path(
        'user-inactivate-service/<str:id>/',
        InactivateUser.as_view(),
        name='user-inactivate'),
    path(
        'user-activate-service/<str:id>/',
        ActivateUser.as_view(),
        name='user-activate'),
    path('logout-servive/', LogoutView.as_view(), name='logout'),
    path('me/', MeView.as_view(), name='me'),

]
