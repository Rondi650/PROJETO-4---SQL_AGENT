# Template Simples de Controle de Acesso

## 📝 O que foi adicionado

Controle de acesso básico que filtra automaticamente queries SQL por operação.

## 📁 Arquivos

1. **my_agent/config/user_permissions.py** - Mapeamento usuário → operações
2. **my_agent/utils/security_nodes.py** - Nó que filtra SQL
3. **exemplo_seguranca_simples.py** - Exemplo de uso

## 🎯 Como funciona

```python
# 1. Configurar usuário em user_permissions.py
USER_PERMISSIONS = {
    "Jairo": ["X"],  # Só pode acessar operação X
}

# 2. Passar user_id no config
config = RunnableConfig(
    configurable={"user_id": "Jairo"}
)

# 3. Query é automaticamente filtrada
# Original: SELECT * FROM tabela
# Filtrada: SELECT * FROM tabela WHERE [Operation] IN ('X')
```

## ▶️ Executar

```bash
python exemplo_seguranca_simples.py
```

## ⚙️ Personalizar

**Adicionar usuário:**
```python
# Em user_permissions.py
USER_PERMISSIONS["NovoUsuario"] = ["Y", "Z"]
```

**Acesso total:**
```python
USER_PERMISSIONS["Admin"] = None  # None = sem restrições
```

**Sem acesso:**
```python
USER_PERMISSIONS["Guest"] = []  # Lista vazia = bloqueado
```

## 🔄 Fluxo

```
START → Roteador → [SQL?] → Add SQL Filter → Valida → Tools → Roteador
                      ↓
                   [Outras Tools] → Tools → Roteador
```

É isso! Template básico pronto para expandir conforme necessário.
