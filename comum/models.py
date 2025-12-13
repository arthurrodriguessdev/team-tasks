from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class Usuario(AbstractUser):
    nome = models.CharField(max_length=120, blank=False, null=False, default='Não informado', help_text='Informe seu nome')
    email = models.EmailField(_("email address"), blank=False)
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
        return self.nome.capitalize()
