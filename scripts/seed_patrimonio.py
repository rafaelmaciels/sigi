import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import date, datetime
from app import create_app, db
from app.models import Patrimonio

app = create_app()

with app.app_context():
    print("Iniciando povoamento do módulo de Patrimônio...")
    Patrimonio.query.delete()

    patrimonios_data = [
        # --- IMÓVEIS ---
        {
            "nome": "Templo Sede Principal (Terreno e Edificação)",
            "descricao": "Prédio próprio com nave para 400 pessoas, 6 salas de EBD, berçário, secretaria geral, gabinete pastoral, banheiros acessíveis e salão social.",
            "categoria": "Imóveis",
            "numero": "PAT-IMO-001",
            "valor": 1250000.00,
            "data_entrada": date(2020, 1, 15),
            "situacao": "Ativo"
        },
        {
            "nome": "Casa Pastoral e Anexo de Acolhimento",
            "descricao": "Residência ministerial anexa com 3 dormitórios, sala de estar, cozinha e garagem para 2 veículos.",
            "categoria": "Imóveis",
            "numero": "PAT-IMO-002",
            "valor": 380000.00,
            "data_entrada": date(2021, 6, 10),
            "situacao": "Ativo"
        },
        {
            "nome": "Terreno Lateral para Estacionamento e Expansão",
            "descricao": "Lote de 450m² pavimentado e murado com portão automático para estacionamento de membros e visitantes.",
            "categoria": "Imóveis",
            "numero": "PAT-IMO-003",
            "valor": 220000.00,
            "data_entrada": date(2023, 3, 20),
            "situacao": "Ativo"
        },

        # --- VEÍCULOS ---
        {
            "nome": "Van Escolar/Passageiros Renault Master 16 Lugares",
            "descricao": "Veículo utilizado para translado de idosos nos cultos de domingo, retiros de jovens e missões regionais. Placa BRA-2024.",
            "categoria": "Veículos",
            "numero": "PAT-VEI-001",
            "valor": 165000.00,
            "data_entrada": date(2024, 2, 18),
            "situacao": "Ativo"
        },
        {
            "nome": "Furgão Utilitário Fiat Fiorino 1.4 Hard Working",
            "descricao": "Veículo para apoio logístico, transporte de cestas básicas da ação social e manutenção predial. Placa SIG-5000.",
            "categoria": "Veículos",
            "numero": "PAT-VEI-002",
            "valor": 72000.00,
            "data_entrada": date(2023, 8, 14),
            "situacao": "Ativo"
        },

        # --- EQUIPAMENTOS ---
        {
            "nome": "Mesa de Som Digital Behringer X32 de 32 Canais",
            "descricao": "Console digital para mixagem do templo sede com gravação multitrack e controle via tablet/Wi-Fi.",
            "categoria": "Equipamentos",
            "numero": "PAT-EQU-001",
            "valor": 22500.00,
            "data_entrada": date(2025, 4, 10),
            "situacao": "Ativo"
        },
        {
            "nome": "Sistema de Caixas Acústicas Line Array JBL VRX932 (4 Unidades)",
            "descricao": "Conjunto de caixas ativas suspensas para sonorização de alta fidelidade na nave do templo.",
            "categoria": "Equipamentos",
            "numero": "PAT-EQU-002",
            "valor": 34000.00,
            "data_entrada": date(2024, 11, 5),
            "situacao": "Ativo"
        },
        {
            "nome": "Subwoofers Ativos JBL SRX828SP Duplo 18 Polegadas (2 Unidades)",
            "descricao": "Graves de alta potência posicionados sob o altar para reforço acústico.",
            "categoria": "Equipamentos",
            "numero": "PAT-EQU-003",
            "valor": 18900.00,
            "data_entrada": date(2024, 11, 5),
            "situacao": "Ativo"
        },
        {
            "nome": "Projetor Laser Epson Pro EX11000 Full HD 4600 Lumens",
            "descricao": "Projetor multimídia para telão central de letras, avisos e transmissões ao vivo.",
            "categoria": "Equipamentos",
            "numero": "PAT-EQU-004",
            "valor": 8900.00,
            "data_entrada": date(2025, 2, 22),
            "situacao": "Ativo"
        },
        {
            "nome": "Câmeras PTZ Robóticas com Zoom Óptico 20x (Kit 2 Unidades)",
            "descricao": "Câmeras motorizadas para transmissão online no YouTube e gravação dos cultos em 4K.",
            "categoria": "Equipamentos",
            "numero": "PAT-EQU-005",
            "valor": 14500.00,
            "data_entrada": date(2025, 6, 12),
            "situacao": "Ativo"
        },
        {
            "nome": "Computador Workstation da Multimídia e Transmissão",
            "descricao": "PC Core i7 13ª Geração, 32GB RAM, Placa RTX 4070, 1TB NVMe, com software vMix e OBS Studio.",
            "categoria": "Equipamentos",
            "numero": "PAT-EQU-006",
            "valor": 9800.00,
            "data_entrada": date(2025, 6, 12),
            "situacao": "Ativo"
        },
        {
            "nome": "Computador Desktop da Secretaria Administrativa",
            "descricao": "PC Core i5, 16GB RAM, SSD 512GB com monitor Dell 24 pol. e leitor de cartões de membros.",
            "categoria": "Equipamentos",
            "numero": "PAT-EQU-007",
            "valor": 4200.00,
            "data_entrada": date(2024, 5, 8),
            "situacao": "Ativo"
        },
        {
            "nome": "Sistema de Ar-Condicionado Split Carrier 60.000 BTUs (Nave 1)",
            "descricao": "Aparelho de climatização central instalado no lado direito da nave principal.",
            "categoria": "Equipamentos",
            "numero": "PAT-EQU-008",
            "valor": 13200.00,
            "data_entrada": date(2025, 5, 25),
            "situacao": "Ativo"
        },
        {
            "nome": "Sistema de Ar-Condicionado Split Carrier 60.000 BTUs (Nave 2)",
            "descricao": "Aparelho de climatização central instalado no lado esquerdo da nave principal.",
            "categoria": "Equipamentos",
            "numero": "PAT-EQU-009",
            "valor": 13200.00,
            "data_entrada": date(2025, 5, 25),
            "situacao": "Ativo"
        },
        {
            "nome": "Gerador de Energia a Diesel Toyama 15kVA Trifásico",
            "descricao": "Grupo gerador com partida automática para emergências e cultos sem interrupção de energia.",
            "categoria": "Equipamentos",
            "numero": "PAT-EQU-010",
            "valor": 26800.00,
            "data_entrada": date(2024, 9, 30),
            "situacao": "Manutenção"
        },
        {
            "nome": "Bateria Acústica Pearl Export Series com Pratos Zildjian",
            "descricao": "Instrumento musical do ministério de louvor com microfonação dedicada e aquário de acrílico acústico.",
            "categoria": "Equipamentos",
            "numero": "PAT-EQU-011",
            "valor": 11500.00,
            "data_entrada": date(2024, 3, 15),
            "situacao": "Ativo"
        },
        {
            "nome": "Teclado Arranjador e Sintetizador Yamaha Motif XF8",
            "descricao": "Piano digital e sintetizador de 88 teclas pesadas para uso ministerial nos cultos e eventos.",
            "categoria": "Equipamentos",
            "numero": "PAT-EQU-012",
            "valor": 16000.00,
            "data_entrada": date(2023, 10, 20),
            "situacao": "Ativo"
        },

        # --- MÓVEIS ---
        {
            "nome": "Púlpito em Acrílico Cristal 15mm com Emblema SiGI Gravado",
            "descricao": "Púlpito moderno de altar com suporte para microfone gooseneck e base de iluminação LED embutida.",
            "categoria": "Móveis",
            "numero": "PAT-MOV-001",
            "valor": 3600.00,
            "data_entrada": date(2025, 1, 20),
            "situacao": "Ativo"
        },
        {
            "nome": "Lote de 250 Cadeiras Estofadas Longarinas Azuis para o Templo",
            "descricao": "Cadeiras com estrutura de aço reforçado e estofamento antichamas para a nave central.",
            "categoria": "Móveis",
            "numero": "PAT-MOV-002",
            "valor": 37500.00,
            "data_entrada": date(2024, 7, 10),
            "situacao": "Ativo"
        },
        {
            "nome": "Mesa de Diretoria Oval em Madeira Maciça com 12 Cadeiras Giratórias",
            "descricao": "Mesa executiva para reuniões de diretoria, assembleias de presbíteros e conselho fiscal.",
            "categoria": "Móveis",
            "numero": "PAT-MOV-003",
            "valor": 8400.00,
            "data_entrada": date(2023, 4, 18),
            "situacao": "Ativo"
        },
        {
            "nome": "Conjunto de Armários de Aço Reforçados e Arquivo Morto (4 Módulos)",
            "descricao": "Armários com chave para guarda de documentos eclesiásticos, livros de atas e certificados.",
            "categoria": "Móveis",
            "numero": "PAT-MOV-004",
            "valor": 4800.00,
            "data_entrada": date(2023, 5, 22),
            "situacao": "Ativo"
        },
        {
            "nome": "Mesas e Carteiras Escolares Infantis para Salas de EBD (30 Conjuntos)",
            "descricao": "Mobiliário infantil colorido e ergonômico para as salas do ministério de crianças.",
            "categoria": "Móveis",
            "numero": "PAT-MOV-005",
            "valor": 5900.00,
            "data_entrada": date(2024, 2, 10),
            "situacao": "Ativo"
        }
    ]

    for pat in patrimonios_data:
        p_obj = Patrimonio(**pat)
        db.session.add(p_obj)

    db.session.commit()

    total_itens = Patrimonio.query.count()
    valor_total = sum(p.valor or 0.0 for p in Patrimonio.query.all())
    print("\n" + "=" * 60)
    print("POVOAMENTO DE PATRIMÔNIO CONCLUÍDO COM SUCESSO!")
    print(f"Total de Bens Cadastrados: {total_itens}")
    print(f"Valor Total do Patrimônio Avaliado: R$ {valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    print("=" * 60)
