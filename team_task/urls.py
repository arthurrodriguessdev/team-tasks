from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('comum.urls')),
    path('tarefas/', include('tarefa.urls')),
    path('equipes/', include('equipe.urls')),
    path('organizacao/', include('organizacao.urls')),
    path('planos/', include('apipagamentos.urls'))
]

# Funções customizadas de páginas de erro
handler403 = 'comum.views.forbidden'
handler404 = 'comum.views.not_found'
handler500 = 'comum.views.server_error'