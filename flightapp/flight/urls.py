from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("register", views.register_view, name="register"),
    path("logout", views.logout_view, name="logout"),
    path('flight/ticket/cancel', views.cancel_ticket, name="cancelticket"),
    path("flight", views.flight, name="flight"),
]
