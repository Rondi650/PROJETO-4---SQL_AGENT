"""
Configuração simples de permissões de usuários
"""

# Mapeamento: usuário -> operações permitidas
USER_PERMISSIONS = {
    "Jairo": ["X"],
    "Maria": ["X", "Y", "Z"],
    "Admin": None  # None = acesso total
}

def get_user_operations(user_id: str) -> list[str] | None:
    """Retorna operações permitidas para o usuário"""
    return USER_PERMISSIONS.get(user_id, [])  # [] = sem acesso
