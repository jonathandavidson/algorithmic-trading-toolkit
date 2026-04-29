from argparse import Namespace
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.orm import Session

from lib.config import load_config, save_config
from lib.database import get_engine
from lib.models.base import Base
from lib.models.historical_bars import HistoricalBar
import lib.models.historical_bars  # registers HistoricalBar with Base.metadata


def cmd_collection_add(args: Namespace) -> None:
    config = load_config()
    collections = config.setdefault("collections", [])
    if any(c["name"] == args.name for c in collections):
        print(f"Collection '{args.name}' already exists.")
        return
    entry = {
        "name": args.name,
        "database": args.database,
        "type": args.type,
        "start": args.start,
    }
    if args.frequency is not None:
        entry["frequency"] = args.frequency
    if args.end is not None:
        entry["end"] = args.end
    collections.append(entry)
    save_config(config)
    print(f"Collection '{args.name}' added.")


def cmd_collection_list(args: Namespace) -> None:
    collections = load_config().get("collections", [])
    if not collections:
        print("No collections configured.")
        return
    for c in collections:
        parts = [
            f"name={c['name']}",
            f"database={c['database']}",
            f"type={c['type']}",
            f"start={c['start']}",
        ]
        if "frequency" in c:
            parts.append(f"frequency={c['frequency']}")
        if "end" in c:
            parts.append(f"end={c['end']}")
        print("  ".join(parts))


def cmd_collection_remove(args: Namespace) -> None:
    config = load_config()
    collections = config.get("collections", [])
    if not any(c["name"] == args.name for c in collections):
        print(f"Collection '{args.name}' not found.")
        return
    answer = input(f"Remove collection '{args.name}'? [y/N] ")
    if answer.strip().lower() != "y":
        print("Cancelled.")
        return
    config["collections"] = [c for c in collections if c["name"] != args.name]
    save_config(config)
    print(f"Collection '{args.name}' removed.")


def cmd_collection_init(args: Namespace) -> None:
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
    answer = input(
        f"Create tables in database '{db['name']}' ({db['host']}:{db['port']}/{db['dbname']})? "
        f"Any existing tables will be dropped and recreated — back up data to avoid losing it. [y/N] "
    )
    if answer.strip().lower() != "y":
        print("Cancelled.")
        return
    engine = get_engine(db)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    print("Tables created.")


def cmd_collection_run(args: Namespace) -> None:
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


def cmd_collection(args: Namespace) -> None:
    if not hasattr(args, "collection_command") or args.collection_command is None:
        args.collection_parser.print_help()
