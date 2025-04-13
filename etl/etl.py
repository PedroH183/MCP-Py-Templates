import os
import logging
import pandas as pd
import psycopg2
from elasticsearch import Elasticsearch, helpers

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("etl_produtos")


def get_postgres_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv("PGHOST"),
            port=os.getenv("PGPORT"),
            user=os.getenv("PGUSER"),
            password=os.getenv("PGPASSWORD"),
            dbname=os.getenv("PGDATABASE"),
        )
        return conn
    except Exception as e:
        raise Exception(f"PostgreSQL service is not available: {e!s}")


def create_postgres_view(pg_conn, cursor):
    cursor.execute(
        """
        CREATE OR REPLACE VIEW vw_produtos_indexados AS
        SELECT 
            pr.productid,
            pr.name,
            pr.productnumber,
            pr.color,
            pr.listprice as list_price,
            pr.size,
            pr.weight,
            pr.safetystocklevel as stock_level,
            pr.productmodelid as product_model_id
        FROM production.product AS pr 
        LEFT JOIN 
            production.productmodel AS pm ON pr.productmodelid = pm.productmodelid
        WHERE 
            1=1
            AND pr.name IS NOT NULL 
            AND pr.listprice <> 0
            AND pr.weight IS NOT NULL
    """
    )
    return pg_conn.commit()


def create_view_if_not_exists(pg_conn):
    """Create the view for products if it doesn't exist"""

    with pg_conn.cursor() as cursor:
        cursor.execute("""
            SELECT FROM pg_views WHERE viewname = 'vw_produtos_indexados' LIMIT 1
        """)
        view_exists = cursor.fetchone()

        if not view_exists:
            logger.info("Creating view vw_produtos_indexados")
            create_postgres_view(pg_conn, cursor)
        else:
            logger.info("View vw_produtos_indexados already exists")


def executar_etl():
    """Extract product data from PostgreSQL and load it into Elasticsearch"""

    pg_conn = get_postgres_connection()
    create_view_if_not_exists(pg_conn)

    logger.info("Extracting product data from PostgreSQL")
    query = "SELECT * FROM vw_produtos_indexados"

    df = pd.read_sql_query(query, pg_conn)
    pg_conn.close()

    if df.empty:
        logger.warning("No product data found in the database")
        return 0

    logger.info("Instanciando a conexão com o elasticsearch")
    es = Elasticsearch(os.getenv("ES_HOST"))
    index_name = "produtos"

    if not es.indices.exists(index=index_name):
        logger.info(f"Criando o index '{index_name}'")
        es.indices.create(index=index_name)
    else:
        logger.info(f"O index '{index_name}' já existe")

    logger.info("Limpando e preparando os dados para o index")
    # Substituindo valores NaN por None (null em JSON)
    df = df.where(pd.notnull(df), None)

    # Tratando casos em que os tipos não são o esperado
    if "list_price" in df.columns:
        df["list_price"] = df["list_price"].astype(float)

    if "weight" in df.columns:
        df["weight"] = df["weight"].apply(lambda x: float(x) if x is not None else None)

    if "stock_level" in df.columns:
        df["stock_level"] = df["stock_level"].astype(int)

    # Preparando os documentos para o index
    def gerar_documentos(df):
        for _, row in df.iterrows():
            # Removendo os valores nulos que vinheram da query
            doc = {}
            [doc.update({k: v}) for k, v in row.to_dict().items() if v is not None]
            yield {"_index": index_name, "_id": row["productid"], "_source": doc}

    # Carregando os dados no Elasticsearch
    logger.info(f"Carregando {len(df)} produtos no Elasticsearch")
    try:
        success, errors = helpers.bulk(
            es, gerar_documentos(df), stats_only=False, raise_on_error=False
        )

        if errors:
            logger.warning(
                f"Carregamento concluído com {len(errors)} erros. {success} produtos indexados com sucesso."
            )
        return success

    except Exception as e:
        logger.error(f"Bulk indexing error: {e}")
        raise


if __name__ == "__main__":
    try:
        logger.info("Starting ETL process")
        num_products = executar_etl()
        logger.info(
            f"ETL process completed successfully. Processed {num_products} products."
        )
    except Exception as e:
        logger.error(f"ETL process failed with error: {e!s}")
