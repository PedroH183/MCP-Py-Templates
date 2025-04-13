# <div align="center"><img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/postgresql/postgresql-original-wordmark.svg" width="100" height="100" alt="AdventureWorks"/></div>

# AdventureWorks for PostgreSQL + Elasticsearch

ETL pipeline para indexar dados do PostgreSQL no Elasticsearch e criar um MCP Server para buscas.

## Objetivo

Subir um ambiente com:
1. PostgreSQL contendo dados da AdventureWorks
2. Elasticsearch para armazenar os dados indexados
3. Serviço ETL para migração dos dados
4. Futuro MCP Server para realizar buscas nos índices

## Stack

<div align="center">
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/Elasticsearch-005571?style=for-the-badge&logo=elasticsearch&logoColor=white" alt="Elasticsearch" />
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker" />
</div>

- PostgreSQL
- Elasticsearch
- Kibana (opcional para visualização)
- Python (ETL)

## Como Executar

1. Clone o repositório
2. Execute:
```bash
docker compose up --build
```

## Estrutura do Projeto

- `etl/`: Contém o código Python do ETL e Dockerfile
  - `etl.py`: Script principal de extração e carga
  - `init/`: Configuração inicial do PostgreSQL
- `docker-compose.yml`: Orquestração dos serviços

## Futuros Passos

1. Implementar o MCP Server para:
   - Receber um índice e texto como entrada
   - Realizar buscas no Elasticsearch
   - Retornar resultados relevantes

## Exemplo de Uso Futuro

```python
from mcp_server import search

results = search(index="produtos", query="bike mountain")
