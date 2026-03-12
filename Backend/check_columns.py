from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = "postgresql://postgres:12345@localhost:5432/aviko"


def check_table_columns():
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)

    tables_to_check = ['target_conversions', 'search_statistics', 'action_log', 'listing_view_statistics']

    for table_name in tables_to_check:
        logger.info(f"\n=== Таблица: {table_name} ===")
        try:
            columns = inspector.get_columns(table_name)
            for col in columns:
                logger.info(f"  {col['name']} - {col['type']}")
        except Exception as e:
            logger.error(f"Ошибка при получении колонок для {table_name}: {e}")

    # Проверяем конкретные колонки через connection
    logger.info("\n=== Детальная проверка колонок с 'date'/'time' ===")

    with engine.connect() as conn:
        # target_conversions
        result = conn.execute(
            text("SELECT column_name FROM information_schema.columns WHERE table_name='target_conversions'")
        )
        columns = [row[0] for row in result]
        logger.info(f"target_conversions columns: {columns}")

        # search_statistics
        result = conn.execute(
            text("SELECT column_name FROM information_schema.columns WHERE table_name='search_statistics'")
        )
        columns = [row[0] for row in result]
        logger.info(f"search_statistics columns: {columns}")

        # action_log
        result = conn.execute(
            text("SELECT column_name FROM information_schema.columns WHERE table_name='action_log'")
        )
        columns = [row[0] for row in result]
        logger.info(f"action_log columns: {columns}")

        # listing_view_statistics
        result = conn.execute(
            text("SELECT column_name FROM information_schema.columns WHERE table_name='listing_view_statistics'")
        )
        columns = [row[0] for row in result]
        logger.info(f"listing_view_statistics columns: {columns}")


if __name__ == "__main__":
    check_table_columns()