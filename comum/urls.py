from django.urls import path
from comum.views import login_usuario, cadastrar_usuario, logout_usuario, vincular_responsaveis, api_dashboard, exibir_dashboard, exibir_onboarding, exibir_codigo_convite_onboarding, convites_onboarding, exibir_dashboard_organizacao, api_organizacao_dashboard, meu_perfil, enviar_email_codigo, suporte_usuario, alterar_senha, cadastrar_nova_senha


urlpatterns = [
    path('', login_usuario, name='login_usuario'),
    path('cadastro/', cadastrar_usuario, name='cadastro_usuario'),
    path('logout/', logout_usuario, name='logout_usuario'),
    path('vincular_responsaveis_tarefa/<int:pk>', vincular_responsaveis, name='vincular_responsaveis_tarefa'),

    path('api_dashboard', api_dashboard, name='dashboard'),
    path('dashboard', exibir_dashboard, name='exibir_dashboard'),

    path('api_organizacao_dashboard', api_organizacao_dashboard, name='dashboard_organizacao'),
    path('dashboard_organizacao', exibir_dashboard_organizacao, name='exibir_dashboard_organizacao'),

    path('onboarding', exibir_onboarding, name='onboarding'),
    path('onboarding/aguardando_convite', exibir_codigo_convite_onboarding, name='exibir_codigo_convite_onboarding'),
    path('onboarding/meus_convites', convites_onboarding, name='meus_convites'),

    path('meu_perfil/', meu_perfil, name='meu_perfil'),
    path('verificacao_email/', enviar_email_codigo, name='enviar_email_codigo'),

    path('suporte/', suporte_usuario, name='suporte_usuario'),
    path('alterar_senha/', alterar_senha, name='alterar_senha'),
    path('credenciais/<str:token>/redefinicao_senha/', cadastrar_nova_senha,name='redefinicao_senha')
]