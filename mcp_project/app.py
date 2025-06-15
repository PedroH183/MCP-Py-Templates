from mcp.server.fastmcp import FastMCP
from typing import Union
from elasticsearch import Elasticsearch


mcp = FastMCP("ElasticLocal")


@mcp.tool("search_elastic_tool")
def search_elastic_tool(query: dict, index: str) -> Union[list[dict], str]:
    """Search Elasticsearch for a query"""

    es = Elasticsearch(
        hosts=["http://localhost:9200"], basic_auth=("elastic", "elastic")
    )
    try:
        res = es.search(index=index, body=query)
    except Exception as e:
        return f"Erro ao consultar Elasticsearch: {e!s}"

    products = res.get("hits", {}).get("hits", [])
    if not products:
        return "No results found"

    return products


if __name__ == "__main__":
    mcp.run(transport="stdio")


# Add a dynamic greeting resource
# @mcp.resource("greeting://{index}")
# def get_greeting(name: str) -> str:
#    """Get a personalized greeting"""
#    return f"Hello, {name}!"
