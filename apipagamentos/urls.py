from apipagamentos.views import adquirir_plano_essencial
from django.urls import path

urlpatterns = [
    path('plano_essencial', adquirir_plano_essencial, name='adquirir_plano_essencial')
]