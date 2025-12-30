from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class Usuario(AbstractUser):
    nome = models.CharField(max_length=120, blank=False, help_text='Informe seu nome')
    email = models.EmailField(blank=False, verbose_name='E-mail', unique=True)

    is_staff = models.BooleanField(
        ("staff status"),
        default=False,
        help_text = 'O usuário pode acessar a administração do site?'
    )

    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text = 'O usuário está ativo?'
    )

    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return f'{self.nome.capitalize()} - {self.username}'
        # return self.nome.capitalize()
    

class MembroEquipe(models.Model):
    equipe = models.ForeignKey('equipe.Equipe', on_delete=models.PROTECT, related_name='membros_equipe')
    membro = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='usuarios_membros')

    def __str__(self):
        return f'{self.membro.nome} - {self.equipe.nome}'
    
    @classmethod
    def get_usuarios_membros_equipe(cls, equipe_id):
        id_membros = cls.objects.filter(equipe=equipe_id).values_list('membro', flat=True)
        queryset = Usuario.objects.filter(id__in=id_membros)

        return queryset