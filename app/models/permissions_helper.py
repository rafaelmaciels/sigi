from flask_login import current_user
from app.models import UserPermission, Permission

def has_permission(area, action):
    if not current_user.is_authenticated:
        return False
    # Se o usuário for admin, sempre tem acesso
    if getattr(current_user, "is_admin", False):
        return True
    # Busca a permissão no banco
    perm = Permission.query.filter_by(area=area, action=action).first()
    if not perm:
        return False
    return UserPermission.query.filter_by(
        user_id=current_user.id,
        permission_id=perm.id
    ).first() is not None
