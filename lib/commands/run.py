from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.orm import Session

from lib.config import load_config
from lib.database import get_engine
from lib.models.historical_bars import HistoricalBar


def cmd_run_collection(args):
    config = load_config()
    collections = config.get("collections", [])
    collection = next((c for c in collections if c["name"] == args.name), None)
    if collection is None:
        print(f"Collection '{args.name}' not found.")
        return
    databases = config.get("databases", [])
    db = next((d for d in databases if d["name"] == collection["database"]), None)
    if db is None:
        print(f"Database '{collection['database']}' not found.")
        return

    engine = get_engine(db)
    now = datetime.now(timezone.utc)

    bars = [
        HistoricalBar(
            id=1,
            collection_name=collection["name"],
            symbol="AAPL",
            time=datetime(2024, 1, 2, 9, 30, tzinfo=timezone.utc),
            open=Decimal("185.0000"),
            high=Decimal("186.5000"),
            low=Decimal("184.2500"),
            close=Decimal("186.1900"),
            volume=45231000,
            trade_count=312400,
            volume_weighted_avg_price=Decimal("185.7500"),
            created_at=now,
            updated_at=now,
        ),
        HistoricalBar(
            id=2,
            collection_name=collection["name"],
            symbol="AAPL",
            time=datetime(2024, 1, 3, 9, 30, tzinfo=timezone.utc),
            open=Decimal("184.2200"),
            high=Decimal("185.8800"),
            low=Decimal("183.4300"),
            close=Decimal("184.9200"),
            volume=53412000,
            trade_count=345600,
            volume_weighted_avg_price=Decimal("184.8100"),
            created_at=now,
            updated_at=now,
        ),
        HistoricalBar(
            id=3,
            collection_name=collection["name"],
            symbol="AAPL",
            time=datetime(2024, 1, 4, 9, 30, tzinfo=timezone.utc),
            open=Decimal("182.1500"),
            high=Decimal("183.9000"),
            low=Decimal("181.5000"),
            close=Decimal("181.9100"),
            volume=47865000,
            trade_count=298700,
            volume_weighted_avg_price=Decimal("182.7300"),
            created_at=now,
            updated_at=now,
        ),
    ]

    with Session(engine) as session:
        session.add_all(bars)
        session.commit()

    print(f"Inserted {len(bars)} records.")


def cmd_run(args):
    if not hasattr(args, "run_command") or args.run_command is None:
        args.run_parser.print_help()
