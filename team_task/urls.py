from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('comum.urls')),
    path('tarefas/', include('tarefa.urls'))
]
