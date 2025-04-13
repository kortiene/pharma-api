from datetime import date, datetime

from pydantic import BaseModel


# --- UTILS ---
def to_bson_safe_dict(model: BaseModel) -> dict:
    data = model.dict()
    for key, value in data.items():
        if isinstance(value, date) and not isinstance(value, datetime):
            data[key] = datetime.combine(value, datetime.min.time())
    return data
