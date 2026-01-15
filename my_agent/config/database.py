from langchain_community.utilities import SQLDatabase

db = SQLDatabase.from_uri(
    "mssql+pyodbc://localhost/Teste_CallCenter?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes",
    include_tables=["01 Call-Center-Dataset"]
)

print(db.get_table_info())  # Para verificar as tabelas carregadas
print()
print(db.run("SELECT TOP 5 * FROM [01 Call-Center-Dataset]"))  # Teste de consulta