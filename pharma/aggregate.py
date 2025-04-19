from datetime import datetime, timedelta
from pymongo.collection import Collection
from typing import List, Dict


# --- Utility Functions for Pharmacy Stock Management ---


def get_products_with_stock(
    products_col: Collection, stocks_col: Collection
) -> List[Dict]:
    """
    Retrieve all products along with their associated stock quantities and locations.

    Args:
        products_col (Collection): MongoDB collection for products.
        stocks_col (Collection): MongoDB collection for stocks.

    Returns:
        List[Dict]: List of product documents enriched with stock data.
    """
    pipeline = [
        {
            "$lookup": {
                "from": stocks_col.name,
                "localField": "id",
                "foreignField": "product_id",
                "as": "stock_info",
            }
        },
        {"$unwind": "$stock_info"},
        {
            "$project": {
                "_id": 0,
                "id": 1,
                "name": 1,
                "category": 1,
                "expiration_date": 1,
                "unit_price": 1,
                "quantity": "$stock_info.quantity",
                "last_update": "$stock_info.last_update",
                "location": "$stock_info.location",
            }
        },
    ]
    return list(products_col.aggregate(pipeline))


def get_products_near_expiry(
    products_col: Collection, months: int = 3
) -> List[Dict]:
    """
    Retrieve products whose expiration date is within a specified number of months.

    Args:
        products_col (Collection): MongoDB collection for products.
        months (int): Number of months to consider as the expiry threshold.

    Returns:
        List[Dict]: List of products expiring soon with remaining days to expiry.
    """
    now = datetime.utcnow()
    limit_date = now + timedelta(days=30 * months)
    pipeline = [
        {"$match": {"expiration_date": {"$lte": limit_date}}},
        {
            "$project": {
                "id": 1,
                "name": 1,
                "expiration_date": 1,
                "jours_restants": {
                    "$divide": [
                        {"$subtract": ["$expiration_date", now]},
                        1000 * 60 * 60 * 24,
                    ]
                },
            }
        },
    ]
    return list(products_col.aggregate(pipeline))


def get_products_below_critical_threshold(
    products_col: Collection,
    thresholds_col: Collection,
    stocks_col: Collection,
) -> List[Dict]:
    """
    Retrieve products whose current stock is below the defined critical threshold.

    Args:
        products_col (Collection): MongoDB collection for products.
        thresholds_col (Collection): MongoDB collection for stock thresholds.
        stocks_col (Collection): MongoDB collection for stocks.

    Returns:
        List[Dict]: List of products below critical stock threshold.
    """
    pipeline = [
        {
            "$lookup": {
                "from": stocks_col.name,
                "localField": "id",
                "foreignField": "product_id",
                "as": "stock",
            }
        },
        {"$unwind": "$stock"},
        {
            "$lookup": {
                "from": thresholds_col.name,
                "localField": "id",
                "foreignField": "product_id",
                "as": "threshold",
            }
        },
        {"$unwind": "$threshold"},
        {
            "$match": {
                "$expr": {
                    "$lt": ["$stock.quantity", "$threshold.critical_stock"]
                }
            }
        },
        {
            "$project": {
                "id": 1,
                "name": 1,
                "quantity": "$stock.quantity",
                "critical_stock": "$threshold.critical_stock",
            }
        },
    ]
    return list(products_col.aggregate(pipeline))


def get_total_stock_value(
    products_col: Collection, stocks_col: Collection
) -> float:
    """
    Calculate the total monetary value of all products currently in stock.

    Args:
        products_col (Collection): MongoDB collection for products.
        stocks_col (Collection): MongoDB collection for stocks.

    Returns:
        float: Total stock value.
    """
    pipeline = [
        {
            "$lookup": {
                "from": stocks_col.name,
                "localField": "id",
                "foreignField": "product_id",
                "as": "stock",
            }
        },
        {"$unwind": "$stock"},
        {
            "$project": {
                "total_value": {
                    "$multiply": ["$unit_price", "$stock.quantity"]
                }
            }
        },
        {
            "$group": {
                "_id": None,
                "valeur_totale_stock": {"$sum": "$total_value"},
            }
        },
    ]
    result = list(products_col.aggregate(pipeline))
    return result[0]["valeur_totale_stock"] if result else 0.0


def get_stock_statistics_by_category(
    products_col: Collection, stocks_col: Collection
) -> List[Dict]:
    """
    Generate stock statistics aggregated by product category.

    Args:
        products_col (Collection): MongoDB collection for products.
        stocks_col (Collection): MongoDB collection for stocks.

    Returns:
        List[Dict]: List of category statistics including product count and total quantity.
    """
    pipeline = [
        {
            "$lookup": {
                "from": stocks_col.name,
                "localField": "id",
                "foreignField": "product_id",
                "as": "stock",
            }
        },
        {"$unwind": "$stock"},
        {
            "$group": {
                "_id": "$category",
                "nombre_de_produits": {"$sum": 1},
                "quantite_totale": {"$sum": "$stock.quantity"},
            }
        },
        {"$sort": {"quantite_totale": -1}},
    ]
    return list(products_col.aggregate(pipeline))
