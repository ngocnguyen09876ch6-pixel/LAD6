== Kiểm tra việc lấy dữ liệu từ API vừa nạp dữ liệu vào PostgreSQL.(RUN 1)
(.venv) PS D:\Lab5_Pipeline> python -c "import pandas as pd; from src.api_client import fetch_all_pages; from src.transform import normalize; from src.load_postgres import upsert_dataframe; rows=fetch_all_pages('orders', page_size=100); print('API rows:', len(rows)); df=normalize(pd.DataFrame(rows)); print('Run 1 result:', upsert_dataframe('orders', df))"
2026-10-12 14:02:57,354 | INFO | src.api_client | resource=orders page=1 rows=100 total_so_far=100
2026-10-12 14:02:57,368 | INFO | src.api_client | resource=orders page=2 rows=100 total_so_far=200
2026-10-12 14:02:57,382 | INFO | src.api_client | resource=orders page=3 rows=100 total_so_far=300
2026-10-12 14:02:57,396 | INFO | src.api_client | resource=orders page=4 rows=100 total_so_far=400
2026-10-12 14:02:57,420 | INFO | src.api_client | resource=orders page=5 rows=100 total_so_far=500
2026-10-12 14:02:57,435 | INFO | src.api_client | resource=orders page=6 rows=100 total_so_far=600
API rows: 600
2026-10-12 14:02:57,862 | INFO | src.load_postgres | UPSERT completed for core.orders: inserted=600, updated=0
Run 1 result: {'inserted': 600, 'updated': 0, 'inserted_or_updated': 600}

====kiểm tra dữ liệu trong PostgreSQL.

(.venv) PS D:\Lab5_Pipeline> python -c "from sqlalchemy import create_engine, text; from src.config import SETTINGS; e=create_engine(SETTINGS.database_url); c=e.connect(); print('After Run 1 COUNT:', c.execute(text('SELECT COUNT(*) FROM core.orders')).scalar_one()); print('After Run 1 DISTINCT:', c.execute(text('SELECT COUNT(DISTINCT order_id) FROM core.orders')).scalar_one()); print('Duplicate PK groups:', c.execute(text('SELECT COUNT(*) FROM (SELECT order_id FROM core.orders GROUP BY order_id HAVING COUNT(*) > 1) AS x')).scalar_one()); c.close(); e.dispose()"
After Run 1 COUNT: 5600
After Run 1 DISTINCT: 5600
Duplicate PK groups: 0

====kết quả Run 2 — chạy nạp dữ liệu lần thứ hai.

(.venv) PS D:\Lab5_Pipeline> python -c "import pandas as pd; from src.api_client import fetch_all_pages; from src.transform import normalize; from src.load_postgres import upsert_dataframe; rows=fetch_all_pages('orders', page_size=100); print('API rows:', len(rows)); df=normalize(pd.DataFrame(rows)); print('Run 2 result:', upsert_dataframe('orders', df))"
2026-10-12 14:06:13,660 | INFO | src.api_client | resource=orders page=1 rows=100 total_so_far=100
2026-10-12 14:06:13,676 | INFO | src.api_client | resource=orders page=2 rows=100 total_so_far=200
2026-10-12 14:06:13,692 | INFO | src.api_client | resource=orders page=3 rows=100 total_so_far=300
2026-10-12 14:06:13,706 | INFO | src.api_client | resource=orders page=4 rows=100 total_so_far=400
2026-10-12 14:06:13,718 | INFO | src.api_client | resource=orders page=5 rows=100 total_so_far=500
2026-10-12 14:06:13,730 | INFO | src.api_client | resource=orders page=6 rows=100 total_so_far=600
API rows: 600
2026-10-12 14:06:14,150 | INFO | src.load_postgres | UPSERT completed for core.orders: inserted=0, updated=600
Run 2 result: {'inserted': 0, 'updated': 600, 'inserted_or_updated': 600}

=== kiểm tra dữ liệu trong PostgreSQL sau khi bạn chạy Run 2.

(.venv) PS D:\Lab5_Pipeline> python -c "from sqlalchemy import create_engine, text; from src.config import SETTINGS; e=create_engine(SETTINGS.database_url); c=e.connect(); print('After Run 2 COUNT:', c.execute(text('SELECT COUNT(*) FROM core.orders')).scalar_one()); print('After Run 2 DISTINCT:', c.execute(text('SELECT COUNT(DISTINCT order_id) FROM core.orders')).scalar_one()); print('Duplicate PK groups:', c.execute(text('SELECT COUNT(*) FROM (SELECT order_id FROM core.orders GROUP BY order_id HAVING COUNT(*) > 1) AS x')).scalar_one()); c.close(); e.dispose()"
After Run 2 COUNT: 5600
After Run 2 DISTINCT: 5600
Duplicate PK groups: 0
(.venv) PS D:\Lab5_Pipelin

