from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from langchain_community.utilities import SQLDatabase

# ODBC string (mais robusto que montar URI na mão)
connection_string = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=Teste_CallCenter;"
    "Trusted_Connection=yes;"
)

connection_url = URL.create(
    "mssql+pyodbc",
    query={"odbc_connect": connection_string}
)

engine = create_engine(connection_url, pool_pre_ping=True)

# Continua usando SQLDatabase (inclusive para Toolkit/Agent depois)
db = SQLDatabase(
    engine=engine,
    include_tables=["01 Call-Center-Dataset"]
)