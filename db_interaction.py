import psycopg2
import os
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv

load_dotenv()



def drop_tables_DB():

    # Establish the connection
    connection = psycopg2.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_DATABASE")
    )

    try:
        # Create a cursor object
        cursor = connection.cursor()

        # Retrieve all table names in the current database
        # We are assuming public schema, modify if a different schema is used
        cursor.execute("""
            SELECT tablename FROM pg_tables WHERE schemaname = 'public'
        """)
        tables = cursor.fetchall()

        # Drop each table
        for table_name, in tables:
            cursor.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE;")
            print(f"Dropped table {table_name}")

        # Commit the changes
        connection.commit()

    except Exception as error:
        print(f"An error occurred: {error}")
        connection.rollback()

    finally:
        # Close the cursor and connection
        cursor.close()
        connection.close()


def create_tables_DB():

    # Establish the connection
    connection = psycopg2.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_DATABASE")
    )

    try:
        # Create a cursor object
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE SPENDINGS (
                DATE TIMESTAMP,
                TELEGRAM_ID BIGINT,
                AMOUNT DECIMAL(10,2),
                PURPOSE VARCHAR(255)
            );
        """)
        print(f"Created table spendings")
        # Commit the changes
        connection.commit()

    except Exception as error:
        print(f"An error occurred: {error}")
        connection.rollback()

    finally:
        # Close the cursor and connection
        cursor.close()
        connection.close()


def add_spending_DB(telegram_id, amount, purpose):
    cet_timezone = pytz.timezone('CET')
    current_date_linz = datetime.now(cet_timezone).strftime('%Y-%m-%d %H:%M:%S')

    # Establish the connection
    connection = psycopg2.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_DATABASE")
    )

    try:
        # Create a cursor object
        cursor = connection.cursor()
        cursor.execute(f"""
            INSERT INTO SPENDINGS (DATE, TELEGRAM_ID, AMOUNT, PURPOSE)
VALUES ('{current_date_linz}', {telegram_id}, {amount}, '{purpose}');
        """)
        print(f"New spending added")
        # Commit the changes
        connection.commit()

    except Exception as error:
        print(f"An error occurred: {error}")
        connection.rollback()

    finally:
        # Close the cursor and connection
        cursor.close()
        connection.close()


def get_user_spending_DB(telegram_id):
    cet_timezone = pytz.timezone('CET')
    today = datetime.now(cet_timezone)
    tomorrow = today + timedelta(days=1)
    first_day_current_month = today.replace(day=1)
    first_day_previous_month = (first_day_current_month - timedelta(days=1)).replace(day=1)
    start_of_week = today - timedelta(days=today.weekday())  # Monday is the start of the week

    # Format dates to strings for SQL queries
    date_tomorrow = tomorrow.strftime('%Y-%m-%d')
    date_first_day_current_month = first_day_current_month.strftime('%Y-%m-%d')
    date_first_day_previous_month = first_day_previous_month.strftime('%Y-%m-%d')
    date_start_of_week = start_of_week.strftime('%Y-%m-%d')

    connection = psycopg2.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_DATABASE")
    )

    try:
        cursor = connection.cursor()

        # Queries are adjusted to ensure they cover all transactions up to the end of today
        # FOOD
        query_previous_month_food = f"""
            SELECT SUM(AMOUNT) FROM SPENDINGS 
            WHERE TELEGRAM_ID = {telegram_id} AND PURPOSE = 'food'
            AND DATE >= '{date_first_day_previous_month}' 
            AND DATE < '{date_first_day_current_month}';
        """
        query_current_month_food = f"""
            SELECT SUM(AMOUNT) FROM SPENDINGS 
            WHERE TELEGRAM_ID = {telegram_id} AND PURPOSE = 'food'
            AND DATE >= '{date_first_day_current_month}' 
            AND DATE < '{date_tomorrow}';
        """
        query_current_week_food = f"""
            SELECT SUM(AMOUNT) FROM SPENDINGS 
            WHERE TELEGRAM_ID = {telegram_id} AND PURPOSE = 'food'
            AND DATE >= '{date_start_of_week}' 
            AND DATE < '{date_tomorrow}';
        """

        # Fetch and convert results
        cursor.execute(query_previous_month_food)
        spending_previous_month_food = float(cursor.fetchone()[0] or 0)

        cursor.execute(query_current_month_food)
        spending_current_month_food = float(cursor.fetchone()[0] or 0)

        cursor.execute(query_current_week_food)
        spending_current_week_food = float(cursor.fetchone()[0] or 0)

        # OTHER
        query_previous_month_other = f"""
            SELECT SUM(AMOUNT) FROM SPENDINGS 
            WHERE TELEGRAM_ID = {telegram_id} AND PURPOSE = 'other'
            AND DATE >= '{date_first_day_previous_month}' 
            AND DATE < '{date_first_day_current_month}';
        """
        query_current_month_other = f"""
            SELECT SUM(AMOUNT) FROM SPENDINGS 
            WHERE TELEGRAM_ID = {telegram_id} AND PURPOSE = 'other'
            AND DATE >= '{date_first_day_current_month}' 
            AND DATE < '{date_tomorrow}';
        """

        # Fetch and convert results
        cursor.execute(query_previous_month_other)
        spending_previous_month_other = float(cursor.fetchone()[0] or 0)

        cursor.execute(query_current_month_other)
        spending_current_month_other = float(cursor.fetchone()[0] or 0)

        return {
        "food" :{
            "Previous Month": spending_previous_month_food,
            "Current Month": spending_current_month_food,
            "Current Week": spending_current_week_food},
        "other":{
            "Previous Month": spending_previous_month_other,
            "Current Month": spending_current_month_other}
        }

    except Exception as error:
        print(f"An error occurred: {error}")
        return {}

    finally:
        cursor.close()
        connection.close()