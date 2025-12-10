from langchain_community.utilities import SQLDatabase

db = SQLDatabase.from_uri(
    "mssql+pyodbc://localhost/Teste_CallCenter?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes",
    include_tables=["01 Call-Center-Dataset"]
)