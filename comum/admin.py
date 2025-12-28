from django.contrib import admin
from comum.models import MembroEquipe
from equipe.models import Equipe

admin.site.register(Equipe)
admin.site.register(MembroEquipe)
