DATASET_QUERIES = {
    "sales": {
        "method": "SALES_QUERY_PLACEHOLDER",
        "payload": {"query": "SALES_QUERY_PLACEHOLDER"},
    },
    "products": {
        "method": "query_thread_data",
        "payload": {"query": "SELECT * FROM produit LIMIT 100"},
    },
    "stock": {
        "method": "STOCK_QUERY_PLACEHOLDER",
        "payload": {"query": "STOCK_QUERY_PLACEHOLDER"},
    },
    "purchases": {
        "method": "PURCHASES_QUERY_PLACEHOLDER",
        "payload": {"query": "PURCHASES_QUERY_PLACEHOLDER"},
    },
    "orders": {
        "method": "query_thread_data",
        "payload": {"query": "SELECT * FROM orders LIMIT 100"},
    },
    "order_items": {
        "method": "query_thread_data",
        "payload": {"query": "SELECT * FROM orditem LIMIT 100"},
    },
}
