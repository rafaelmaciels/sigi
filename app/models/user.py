from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
from flask_login import UserMixin

# -----------------------------
# 👤 Usuário (Admin / Login)
# -----------------------------
class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    nome = db.Column(db.String(100), nullable=True)
    ativo = db.Column(db.Boolean, default=True)   # ativar/desativar usuário
    foto = db.Column(db.String(255), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)  # 🔹 define se é administrador

    # Relacionamento com permissões
    user_permissions = db.relationship(
        "UserPermission",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy=True
    )

    # Define a senha
    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    # Verifica a senha
    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    # 🔹 Verifica se o usuário possui determinada permissão
    def has_permission(self, area: str, action: str) -> bool:
        if self.is_admin:  # admin sempre tem acesso
            return True
        return any(
            up.permission.area == area and up.permission.action == action
            for up in self.user_permissions
        )

    def __repr__(self) -> str:
        return f"<User {self.email}>"


# -----------------------------
# 📜 Permissões disponíveis
# -----------------------------
class Permission(db.Model):
    __tablename__ = "permissions"

    id = db.Column(db.Integer, primary_key=True)
    area = db.Column(db.String(50), nullable=False)   # exemplo: "usuarios"
    action = db.Column(db.String(50), nullable=False) # exemplo: "view"

    def __repr__(self) -> str:
        return f"<Permission {self.area}:{self.action}>"


# -----------------------------
# 🔗 Relação Usuário ↔ Permissão
# -----------------------------
class UserPermission(db.Model):
    __tablename__ = "user_permissions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    permission_id = db.Column(db.Integer, db.ForeignKey("permissions.id"), nullable=False)

    # Relacionamento com User e Permission
    user = db.relationship("User", back_populates="user_permissions")
    permission = db.relationship("Permission", backref="user_permissions", lazy=True)

    def __repr__(self) -> str:
        return f"<UserPermission user={self.user_id} perm={self.permission_id}>"
