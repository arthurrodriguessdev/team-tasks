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
    codigo = models.CharField(max_length=6, blank=True, null=True, unique=True) #TO DO: Verificar se PODE ficar em branco e nulo mesmo
    email_verificado = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return f'{self.nome.title()} ({self.username})'

    @property
    def tem_organizacao(self):
        return self.organizacoes.filter(membro=self).exists()
    
    @property
    def eh_proprietario_organizacao(self):
        return self.organizacoes.filter(papel='proprietario', membro=self).exists()
    
    @property
    def eh_administrador_organizacao(self):
        return self.organizacoes.filter(papel='proprietario', membro=self).exiss()
    
    @property
    def get_nome(self):
        return self.nome.title()
    
    @property
    def tem_email_verificado(self):
        return self.email_verificado
    

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
    
    @classmethod
    def get_equipe_usuario(cls, usuario):
        from equipe.models import Equipe
        
        id_equipes = cls.objects.filter(membro=usuario).values_list('equipe', flat=True)
        return Equipe.objects.filter(id__in=id_equipes)
    

class CodigoEmail(models.Model):
    codigo_verificacao = models.CharField(max_length=6)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='codigo_usuario')

    def __str__(self):
        return f'{self.usuario.nome} ({self.codigo_verificacao})'

class TokenAlterarSenha(models.Model):
    token_codigo = models.CharField(max_length=8)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='token')
    validade = models.DateTimeField(blank=True, null=True)