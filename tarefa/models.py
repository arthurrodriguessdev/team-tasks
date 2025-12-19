from django.db import models
from comum.models import Usuario, Equipe

class Tarefa(models.Model):
    STATUS = [
        ('criada', 'Criada'),
        ('em_andamento', 'Em andamento'),
        ('finalizada', 'Finalizada')
    ]

    criada_por = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='usuario_criador_tarefa')
    titulo = models.CharField(max_length=100, null=False, blank=False)
    descricao = models.TextField()
    prazo = models.DateField(null=True, blank=True)
    status = models.CharField(choices=STATUS, default=STATUS[0])
    criada_em = models.DateTimeField(auto_now_add=True)
    equipe = models.ForeignKey(Equipe, on_delete=models.PROTECT, related_name='tarefa_equipe', blank=True, null=True)
    responsaveis = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='responsaveis_tarefa')

    def __str__(self):
        return self.titulo


