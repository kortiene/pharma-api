from datetime import datetime, timedelta
from typing import List, Dict, Any
from pymongo.collection import Collection


class StockAggregations:
    """Utility class containing all stock management related aggregations."""

    @staticmethod
    def get_pre_order_forecast(
        movements_col: Collection,
        products_col: Collection,
        months: int = 3
    ) -> List[Dict[str, Any]]:
        """Get consumption forecast for products based on historical data."""
        cutoff_date = datetime.utcnow() - timedelta(days=30 * months)
        pipeline = [
            {"$match": {
                "movement_type": "SORTIE",
                "date": {"$gte": cutoff_date}
            }},
            {"$group": {
                "_id": "$product_id",
                "total_consumption": {"$sum": "$quantity"},
                "movement_count": {"$sum": 1}
            }},
            {"$lookup": {
                "from": products_col.name,
                "localField": "_id",
                "foreignField": "id",
                "as": "product_info"
            }},
            {"$unwind": "$product_info"},
            {"$project": {
                "product_id": "$_id",
                "average_consumption": {
                    "$divide": ["$total_consumption", "$movement_count"]
                },
                "category": "$product_info.category"
            }}
        ]
        return list(movements_col.aggregate(pipeline))

    @staticmethod
    def get_critical_threshold_alerts(
        stocks_col: Collection,
        thresholds_col: Collection
    ) -> List[Dict[str, Any]]:
        """Get products that are below their critical stock threshold."""
        pipeline = [
            {"$lookup": {
                "from": thresholds_col.name,
                "localField": "product_id",
                "foreignField": "product_id",
                "as": "threshold"
            }},
            {"$unwind": "$threshold"},
            {"$match": {
                "$expr": {"$lt": ["$quantity", "$threshold.critical_stock"]}
            }},
            {"$project": {
                "product_id": 1,
                "current_stock": "$quantity",
                "critical_threshold": "$threshold.critical_stock"
            }}
        ]
        return list(stocks_col.aggregate(pipeline))

    @staticmethod
    def verify_deliveries(
        movements_col: Collection,
        products_col: Collection,
        tolerance: float = 0.05
    ) -> List[Dict[str, Any]]:
        """Verify received deliveries against expected quantities."""
        pipeline = [
            {"$match": {"movement_type": "ENTREE"}},
            {"$group": {
                "_id": "$product_id",
                "total_received": {"$sum": "$quantity"},
                "delivery_count": {"$sum": 1}
            }},
            {"$lookup": {
                "from": products_col.name,
                "localField": "_id",
                "foreignField": "id",
                "as": "product_info"
            }},
            {"$unwind": "$product_info"},
            {"$project": {
                "product_id": "$_id",
                "total_received": 1,
                "batch_number": "$product_info.batch_number",
                "expiration_date": "$product_info.expiration_date"
            }}
        ]
        return list(movements_col.aggregate(pipeline))

    @staticmethod
    def get_expiring_products(
        products_col: Collection,
        stocks_col: Collection,
        days_limit: int = 30
    ) -> List[Dict[str, Any]]:
        """Get products that are expiring soon."""
        limit_date = datetime.utcnow() + timedelta(days=days_limit)
        pipeline = [
            {"$match": {
                "expiration_date": {"$lte": limit_date}
            }},
            {"$lookup": {
                "from": stocks_col.name,
                "localField": "id",
                "foreignField": "product_id",
                "as": "stock_info"
            }},
            {"$unwind": "$stock_info"},
            {"$project": {
                "product_id": "$id",
                "name": 1,
                "expiration_date": 1,
                "current_stock": "$stock_info.quantity",
                "days_until_expiry": {
                    "$divide": [
                        {"$subtract": ["$expiration_date", datetime.utcnow()]},
                        24 * 60 * 60 * 1000
                    ]
                }
            }}
        ]
        return list(products_col.aggregate(pipeline))

    @staticmethod
    def generate_inventory_report(
        products_col: Collection,
        stocks_col: Collection
    ) -> List[Dict[str, Any]]:
        """Generate inventory report grouped by category."""
        pipeline = [
            {"$lookup": {
                "from": stocks_col.name,
                "localField": "id",
                "foreignField": "product_id",
                "as": "stock_info"
            }},
            {"$unwind": "$stock_info"},
            {"$group": {
                "_id": "$category",
                "total_products": {"$sum": 1},
                "total_quantity": {"$sum": "$stock_info.quantity"},
                "products": {
                    "$push": {
                        "product_id": "$id",
                        "name": "$name",
                        "quantity": "$stock_info.quantity"
                    }
                }
            }}
        ]
        return list(products_col.aggregate(pipeline))

    @staticmethod
    def get_replenishment_suggestions(
        products_col: Collection,
        stocks_col: Collection,
        thresholds_col: Collection
    ) -> List[Dict[str, Any]]:
        """Get suggestions for products that need replenishment."""
        pipeline = [
            {"$lookup": {
                "from": stocks_col.name,
                "localField": "id",
                "foreignField": "product_id",
                "as": "stock_info"
            }},
            {"$unwind": "$stock_info"},
            {"$lookup": {
                "from": thresholds_col.name,
                "localField": "id",
                "foreignField": "product_id",
                "as": "threshold"
            }},
            {"$unwind": "$threshold"},
            {"$match": {
                "$expr": {"$lt": ["$stock_info.quantity", "$threshold.minimum_stock"]}
            }},
            {"$project": {
                "product_id": "$id",
                "current_stock": "$stock_info.quantity",
                "minimum_stock": "$threshold.minimum_stock",
                "suggested_quantity": {
                    "$subtract": ["$threshold.minimum_stock", "$stock_info.quantity"]
                }
            }}
        ]
        return list(products_col.aggregate(pipeline))

    @staticmethod
    def generate_performance_report(
        movements_col: Collection,
        products_col: Collection
    ) -> List[Dict[str, Any]]:
        """Generate performance report with top products and stockouts."""
        pipeline = [
            {"$match": {"movement_type": {"$in": ["SORTIE", "RUPTURE"]}}},
            {"$group": {
                "_id": "$product_id",
                "total_exits": {
                    "$sum": {
                        "$cond": [
                            {"$eq": ["$movement_type", "SORTIE"]},
                            "$quantity",
                            0
                        ]
                    }
                },
                "total_ruptures": {
                    "$sum": {
                        "$cond": [
                            {"$eq": ["$movement_type", "RUPTURE"]},
                            1,
                            0
                        ]
                    }
                }
            }},
            {"$lookup": {
                "from": products_col.name,
                "localField": "_id",
                "foreignField": "id",
                "as": "product_info"
            }},
            {"$unwind": "$product_info"},
            {"$project": {
                "product_id": "$_id",
                "name": "$product_info.name",
                "category": "$product_info.category",
                "total_exits": 1,
                "total_ruptures": 1
            }},
            {"$sort": {"total_exits": -1}},
            {"$limit": 5}
        ]
        return list(movements_col.aggregate(pipeline))