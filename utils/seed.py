# app/utils/seed.py
from app.models import Permission
from app.extensions import db

def seed_permissions():
    """Popula a tabela de permissões básicas se ainda estiver vazia."""
    perms = [
        # Configurações
        ("config", "view"), ("config", "edit"), ("config", "delete"),

        # Usuários
        ("usuarios", "view"), ("usuarios", "create"), ("usuarios", "edit"), ("usuarios", "delete"),

        # Financeiro
        ("financeiro", "view"), ("financeiro", "create"), ("financeiro", "edit"), ("financeiro", "delete"),

        # Mail / Email
        ("mail", "view"), ("mail", "create"), ("mail", "edit"), ("mail", "delete"),

        # Atas
        ("atas", "view"), ("atas", "create"), ("atas", "edit"), ("atas", "delete"),

        # Cartas
        ("cartas", "view"), ("cartas", "create"), ("cartas", "edit"), ("cartas", "delete"),

        # Certificados
        ("certificados", "view"), ("certificados", "create"), ("certificados", "edit"), ("certificados", "delete"),

        # Eventos
        ("eventos", "view"), ("eventos", "create"), ("eventos", "edit"), ("eventos", "delete"),

        # Membros
        ("membros", "view"), ("membros", "create"), ("membros", "edit"), ("membros", "delete"),

        # Patrimônios
        ("patrimonios", "view"), ("patrimonios", "create"), ("patrimonios", "edit"), ("patrimonios", "delete"),

        # Perfil
        ("perfil", "view"), ("perfil", "password"),
    ]

    if Permission.query.count() == 0:  # 🔹 só roda se estiver vazio
        for area, action in perms:
            db.session.add(Permission(area=area, action=action))
        db.session.commit()
        print("✅ Permissões básicas populadas com sucesso!")
    else:
        print("ℹ️ Permissões já existem, nada foi alterado.")
