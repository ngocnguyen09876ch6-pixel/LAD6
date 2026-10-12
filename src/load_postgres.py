
import pandas as pd
from sqlalchemy import create_engine, text

from src.config import SETTINGS
from src.logger import get_logger


log = get_logger(__name__)

PK_MAPPING = {
    "customers": "customer_id",
    "products": "product_id",
    "orders": "order_id",
    "order_items": "order_item_id",
    "payments": "payment_id",
    "categories": "category_id",
}

engine = create_engine(
    SETTINGS.database_url,
    pool_pre_ping=True,
)


def upsert_dataframe(name: str, df: pd.DataFrame) -> dict:
    if name not in PK_MAPPING:
        raise ValueError(f"Unsupported table: {name}")

    pk = PK_MAPPING[name]

    df = df.copy()
    df = df.astype(object).where(pd.notna(df), None)

    if df.empty:
        return {
            "inserted": 0,
            "updated": 0,
            "inserted_or_updated": 0,
        }

    if pk not in df.columns:
        raise ValueError(
            f"DataFrame missing primary key column: {pk}"
        )

    if df[pk].isna().any():
        raise ValueError(
            f"DataFrame contains missing primary key values: {pk}"
        )

    if df[pk].duplicated().any():
        raise ValueError(
            f"DataFrame contains duplicate primary key values: {pk}"
        )

    cols = list(df.columns)
    records = df.to_dict(orient="records")
    incoming_ids = set(df[pk].tolist())

    update_cols = [
        col for col in cols
        if col not in (pk, "created_at")
    ]

    if not update_cols:
        raise ValueError(
            "DataFrame must contain at least one non-primary-key column"
        )

    columns_sql = ", ".join(cols)

    values_sql = ", ".join(
        f":{col}" for col in cols
    )

    update_sql = ", ".join(
        f"{col} = EXCLUDED.{col}"
        for col in update_cols
    )

    select_sql = text(
        f"""
        SELECT {pk}
        FROM core.{name}
        WHERE {pk} = ANY(:ids)
        """
    )

    upsert_sql = text(
        f"""
        INSERT INTO core.{name} ({columns_sql})
        VALUES ({values_sql})
        ON CONFLICT ({pk})
        DO UPDATE SET {update_sql}
        """
    )

    with engine.begin() as conn:
        result = conn.execute(
            select_sql,
            {"ids": list(incoming_ids)},
        )

        existing_ids = set(result.scalars().all())

        new_ids = incoming_ids - existing_ids
        update_ids = incoming_ids & existing_ids

        inserted = len(new_ids)
        updated = len(update_ids)

        conn.execute(upsert_sql, records)

    
    log.info(
        "UPSERT completed for core.%s: inserted=%s, updated=%s",
        name,
        inserted,
        updated,
    )

    return {
        "inserted": inserted,
        "updated": updated,
        "inserted_or_updated": inserted + updated,
    }
