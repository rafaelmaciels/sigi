#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📜 Povoamento Inicial do Changelog do SiGI
Alimenta a tabela 'changelogs' com o histórico real dos commits e implementações do repositório Git.
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from datetime import date
from app.extensions import db
from app.models import User, Changelog

HISTORICO_REAL_GIT = [
    {
        "data": date(2026, 9, 3),
        "titulo": "Obrigatoriedade de contato, integração WhatsApp e correção no filtro de membros inativos",
        "modulo": "Secretaria & Membros",
        "tipo": "Melhoria",
        "versao": "v4.2",
        "descricao": "Tornou obrigatório o preenchimento de telefone e e-mail no cadastro de membros, adicionou a opção indicativa de número com WhatsApp e corrigiu o filtro de busca de membros inativos na listagem da secretaria.",
        "finalidade": "Assegurar que a secretaria mantenha dados de comunicação atualizados e válidos para avisos e comunicados ministeriais, além de garantir relatórios precisos de membros afastados.",
        "autor_nome": "Rafael Maciel"
    },
    {
        "data": date(2026, 9, 3),
        "titulo": "Implantação do Modo Escuro (Dark Mode) e Seletor de Tema",
        "modulo": "Configurações & Segurança",
        "tipo": "Nova funcionalidade",
        "versao": "v4.2",
        "descricao": "Desenvolveu o suporte completo ao tema escuro em todo o sistema com motor Anti-FOUC (sem piscar a tela na inicialização), paleta HSL balanceada e botões dedicados de seleção de tema claro/escuro em Configurações Gerais.",
        "finalidade": "Proporcionar maior conforto visual durante o uso noturno ou prolongado do sistema por líderes, secretários e tesoureiros.",
        "autor_nome": "Rafael Maciel"
    },
    {
        "data": date(2026, 9, 3),
        "titulo": "Numeração automática de carteirinhas de membros e tombamento de patrimônio",
        "modulo": "Secretaria & Membros",
        "tipo": "Nova funcionalidade",
        "versao": "v4.1",
        "descricao": "Implantou rotina que gera automaticamente o número da credencial do membro com validade padrão de 365 dias e estruturou a numeração de tombamento sequencial organizada por categoria de patrimônio.",
        "finalidade": "Eliminar a necessidade de controle manual de numeração de credenciais e evitar duplicidade no inventário de bens da igreja.",
        "autor_nome": "Rafael Maciel"
    },
    {
        "data": date(2026, 9, 3),
        "titulo": "Visualização interativa da agenda com calendário FullCalendar",
        "modulo": "Eventos & Calendário",
        "tipo": "Nova funcionalidade",
        "versao": "v4.1",
        "descricao": "Integrou o componente FullCalendar na página de eventos, permitindo visualizar cultos, reuniões e programações ministeriais em modos mensal, semanal e diário com cores por categoria.",
        "finalidade": "Oferecer à liderança e membros uma visão panorâmica e intuitiva das atividades e programações da igreja.",
        "autor_nome": "Rafael Maciel"
    },
    {
        "data": date(2026, 9, 3),
        "titulo": "Correção na geração de cartas pastorais e relatórios em PDF",
        "modulo": "Secretaria & Membros",
        "tipo": "Correção",
        "versao": "v4.1",
        "descricao": "Corrigiu rotas e parâmetros no serviço de exportação de cartas de recomendação e relatórios estatísticos, eliminando ocorrências de TypeError e 404 BuildError.",
        "finalidade": "Garantir a estabilidade e a emissão sem erros de documentos impressos e digitais da secretaria.",
        "autor_nome": "Rafael Maciel"
    },
    {
        "data": date(2026, 9, 3),
        "titulo": "Otimização da barra de navegação superior e proteção do layout",
        "modulo": "Geral / Sistema",
        "tipo": "Ajuste",
        "versao": "v4.0",
        "descricao": "Reorganizou a barra de navegação (navbar) com espaçamentos otimizados, protegendo a logo oficial contra encolhimento e agrupando as opções de escalas dentro do menu Eventos.",
        "finalidade": "Melhorar a ergonomia de navegação em computadores e notebooks com telas menores, evitando quebras visuais na barra superior.",
        "autor_nome": "Rafael Maciel"
    },
    {
        "data": date(2026, 9, 2),
        "titulo": "Reformulação executiva da Tesouraria com Ações Rápidas e Extrato Analítico",
        "modulo": "Financeiro",
        "tipo": "Melhoria",
        "versao": "v4.0",
        "descricao": "Redesenhou a interface do módulo financeiro implementando centro de comando unificado com resumo de saldos, atalhos de ações rápidas, segregação de receitas/despesas e extrato detalhado com conciliação.",
        "finalidade": "Agilizar o fluxo de trabalho da tesouraria, fornecendo dados financeiros em tempo real com maior clareza e transparência.",
        "autor_nome": "Rafael Maciel"
    },
    {
        "data": date(2026, 9, 2),
        "titulo": "Módulo corporativo de Escalas de Obreiros e Voluntários",
        "modulo": "Escalas & Voluntários",
        "tipo": "Nova funcionalidade",
        "versao": "v4.0",
        "descricao": "Criou toda a infraestrutura para gestão de equipes ministeriais (Louvor, Diaconia, Infantil, Mídia), funções, geração de escalas por culto, registro de confirmação e sistema de substituições.",
        "finalidade": "Automatizar a organização de equipes e voluntários nos cultos e eventos da igreja, prevenindo faltas e conflitos de horários.",
        "autor_nome": "Rafael Maciel"
    },
    {
        "data": date(2026, 9, 2),
        "titulo": "Novo Dashboard Executivo com Centro de Comando e Gráficos Gerenciais",
        "modulo": "Dashboard",
        "tipo": "Melhoria",
        "versao": "v4.0",
        "descricao": "Reformulou o painel de entrada com indicadores-chave em tempo real, painel de próximas escalas, aniversariantes em destaque e gráficos comparativos de membros e finanças.",
        "finalidade": "Permitir que pastores e líderes tomem decisões embasadas em indicadores consolidados logo ao efetuar login no sistema.",
        "autor_nome": "Rafael Maciel"
    },
    {
        "data": date(2026, 9, 2),
        "titulo": "Busca inteligente com autocomplete no Livro de Atas",
        "modulo": "Documentos",
        "tipo": "Melhoria",
        "versao": "v3.9",
        "descricao": "Implementou preenchimento automático em tempo real na busca de atas ministeriais com pesquisa tolerante a termos e destaques de tópicos deliberados.",
        "finalidade": "Facilitar a consulta rápida a registros históricos e decisões administrativas tomadas pela liderança da igreja.",
        "autor_nome": "Rafael Maciel"
    },
    {
        "data": date(2026, 8, 30),
        "titulo": "Preenchimento automático de endereço via CEP e busca resiliente",
        "modulo": "Geral / Sistema",
        "tipo": "Melhoria",
        "versao": "v3.8",
        "descricao": "Integrou consulta instantânea de endereços pela API ViaCEP no cadastro de membros e dados da igreja, com sistema de contingência/cache contra instabilidades de conexão externa.",
        "finalidade": "Reduzir o tempo de preenchimento dos formulários de cadastro e padronizar os dados de endereços da membresia.",
        "autor_nome": "Rafael Maciel"
    },
    {
        "data": date(2026, 8, 30),
        "titulo": "Gestão do status de transferência de membros e métricas de membresia",
        "modulo": "Secretaria & Membros",
        "tipo": "Melhoria",
        "versao": "v3.8",
        "descricao": "Adicionou o status 'Transferido' para controle do ciclo de vida ministerial e incorporou contadores dinâmicos no painel principal.",
        "finalidade": "Acompanhar com precisão o crescimento orgânico da congregação e a movimentação de membros entre igrejas.",
        "autor_nome": "Rafael Maciel"
    },
    {
        "data": date(2026, 8, 28),
        "titulo": "Implantação do módulo corporativo de Escola Bíblica Dominical (EBD)",
        "modulo": "Escola Dominical (EBD)",
        "tipo": "Nova funcionalidade",
        "versao": "v3.7",
        "descricao": "Desenvolveu a estrutura completa da EBD no sistema: períodos letivos, turmas divididas por faixas etárias, matrículas, chamadas com controle de frequência de alunos e portal 'Minhas Classes' para professores.",
        "finalidade": "Capacitar a superintendência da EBD a gerenciar o ensino bíblico com dados concretos de assiduidade e crescimento de alunos.",
        "autor_nome": "Rafael Maciel"
    },
    {
        "data": date(2026, 8, 28),
        "titulo": "Editor de texto rico (WYSIWYG) com proteção contra ataques XSS",
        "modulo": "Documentos",
        "tipo": "Melhoria",
        "versao": "v3.6",
        "descricao": "Integrou o editor Quill nos campos de atas, relatórios e observações, com mecanismo de sanitização via Bleach para prevenir vulnerabilidades de Cross-Site Scripting.",
        "finalidade": "Possibilitar a formatação de textos, tópicos e notas pastorais com total segurança contra injeção de scripts maliciosos.",
        "autor_nome": "Rafael Maciel"
    },
    {
        "data": date(2026, 8, 28),
        "titulo": "Vínculo 1:1 entre membros e usuários do sistema com perfis restritos",
        "modulo": "Configurações & Segurança",
        "tipo": "Nova funcionalidade",
        "versao": "v3.5",
        "descricao": "Criou funcionalidade que permite promover um membro cadastrado a operador do sistema sem duplicar cadastro, associando-o a perfis seguros (como professor de EBD ou líder de escala).",
        "finalidade": "Descentralizar a operação do sistema com segurança, permitindo que líderes atualizem suas áreas específicas sem acesso a dados confidenciais.",
        "autor_nome": "Rafael Maciel"
    },
    {
        "data": date(2026, 8, 28),
        "titulo": "Ferramentas automatizadas de atualização, backup e diagnósticos",
        "modulo": "Configurações & Segurança",
        "tipo": "Nova funcionalidade",
        "versao": "v3.4",
        "descricao": "Disponibilizou os utilitários de servidor update.py, backup.py e healthcheck.py para sincronização de schemas, rotinas automáticas de dump e monitoramento do ambiente de hospedagem.",
        "finalidade": "Garantir alta confiabilidade na operação do sistema em servidores de produção com facilidade de manutenção e segurança dos dados.",
        "autor_nome": "Rafael Maciel"
    },
    {
        "data": date(2026, 8, 28),
        "titulo": "Envio de certificados via WhatsApp e impressão formatada",
        "modulo": "Documentos",
        "tipo": "Melhoria",
        "versao": "v3.3",
        "descricao": "Adicionou recurso de impressão direta de certificados eclesiásticos (batismo, consagração, apresentação) com link de compartilhamento rápido via WhatsApp.",
        "finalidade": "Facilitar a emissão e entrega ágil de certificados oficiais para membros e famílias da igreja.",
        "autor_nome": "Rafael Maciel"
    },
    {
        "data": date(2026, 8, 28),
        "titulo": "Reforço no controle de permissões por perfil (RBAC) e proteção do Dashboard",
        "modulo": "Configurações & Segurança",
        "tipo": "Melhoria",
        "versao": "v3.2",
        "descricao": "Estruturou o controle granular de visualização e ações por área ministerial, restringindo dados contábeis e administrativos confidenciais a perfis autorizados.",
        "finalidade": "Proteger a privacidade dos dados da igreja e cumprir boas práticas de governança eclesiástica.",
        "autor_nome": "Rafael Maciel"
    },
    {
        "data": date(2026, 1, 10),
        "titulo": "Implantação da arquitetura fundamental do SiGI",
        "modulo": "Geral / Sistema",
        "tipo": "Nova funcionalidade",
        "versao": "v1.0",
        "descricao": "Desenvolvimento da base arquitetural do sistema com Flask, SQLAlchemy, autenticação segura de usuários, cadastros preliminares da secretaria e dízimos da tesouraria.",
        "finalidade": "Estabelecer o núcleo operacional da plataforma de gestão ministerial e eclesiástica da igreja.",
        "autor_nome": "Paulo Soares"
    }
]

def seed_changelog():
    """Popula a tabela de changelogs com o histórico real verificado no Git."""
    # Busca usuário do Rafael Maciel se existir
    usuario_rafael = User.query.filter(
        (User.email == "rafael@sigi.com") | (User.nome.ilike("%Rafael%"))
    ).first()

    inseridos = 0
    for item in HISTORICO_REAL_GIT:
        existente = Changelog.query.filter_by(
            titulo=item["titulo"],
            data_implantacao=item["data"]
        ).first()

        if not existente:
            user_id = None
            if item["autor_nome"] == "Rafael Maciel" and usuario_rafael:
                user_id = usuario_rafael.id

            novo = Changelog(
                titulo=item["titulo"],
                modulo=item["modulo"],
                tipo=item["tipo"],
                versao=item["versao"],
                descricao=item["descricao"],
                finalidade=item["finalidade"],
                data_implantacao=item["data"],
                usuario_id=user_id,
                autor_nome=item["autor_nome"]
            )
            db.session.add(novo)
            inseridos += 1

    if inseridos > 0:
        db.session.commit()
        print(f"[OK] {inseridos} registros reais inseridos no Changelog com sucesso!")
    else:
        print("[INFO] Todos os registros do histórico do Changelog já existem no banco.")

if __name__ == "__main__":
    from app import create_app
    app = create_app()
    with app.app_context():
        db.create_all()
        seed_changelog()
