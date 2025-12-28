from django.db import models
from comum.models import Usuario
from equipe.models import Equipe

class Tarefa(models.Model):
    STATUS = [
        ('criada', 'Criada'),
        ('em_andamento', 'Em andamento'),
        ('finalizada', 'Finalizada')
    ]

    criada_por = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='usuario_criador_tarefa')
    titulo = models.CharField(max_length=100, null=False, blank=False, verbose_name='Título')
    descricao = models.TextField(verbose_name='Descrição da tarefa')
    prazo = models.DateField(null=True, blank=True, verbose_name='Prazo de entrega')
    status = models.CharField(choices=STATUS, default='criada')
    criada_em = models.DateTimeField(auto_now_add=True)
    equipe = models.ForeignKey(Equipe, on_delete=models.PROTECT, related_name='tarefa_equipe', blank=True, null=True)
    responsaveis = models.ManyToManyField(
        Usuario, 
        related_name='responsaveis_tarefa', 
        verbose_name='Responsáveis',
        blank=True,
    ) 

    em_equipe = models.BooleanField(
        verbose_name='Tarefa de equipe',
        null=True,
        blank=True)

    def __str__(self):
        return self.titulo


