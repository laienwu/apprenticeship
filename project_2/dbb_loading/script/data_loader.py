import os
from pathlib import Path
from dotenv import load_dotenv
import csv, json
from pymongo import MongoClient
from sqlalchemy import create_engine, String, Integer
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, Mapped, mapped_column

cust_csv = Path('../data/clients.csv')
products_csv = Path('../data/products.csv')
transactions_csv = Path('../data/transactions.csv')
cust_json = Path('../data/clients.json')
products_json = Path('../data/produits_sous-categorie.json')
transactions_json = Path('../data/ventes.json')

Base = declarative_base()


# Clients table
class Client(Base):
    __tablename__ = "clients"
    client_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    sex: Mapped[str] = mapped_column(String(10))
    birth: Mapped[str] = mapped_column(String(10))

    def __repr__(self) -> str:
        return f"Client(client_id={self.client_id!r}, sex={self.sex!r}, birth={self.birth!r})"


# The Products table
class Product(Base):
    __tablename__ = "products"
    product_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    category: Mapped[str] = mapped_column(String(50))
    sub_category: Mapped[str] = mapped_column(String(50))
    price: Mapped[str] = mapped_column(String(20))
    stock_quantity: Mapped[str] = mapped_column(String(20))

    def __repr__(self) -> str:
        return (f"Product(product_id={self.product_id!r}, category={self.category!r}, "
                f"sub_category={self.sub_category!r}, price={self.price!r}, stock_quantity={self.stock_quantity!r})")


# The Transactions table
# todo Add ForeignKey relationship with ad-hoc constraints for the data.
class Transaction(Base):
    __tablename__ = "transactions"
    transaction_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[str] = mapped_column(String(20))
    date: Mapped[str] = mapped_column(String(50))
    session_id: Mapped[str] = mapped_column(String(10))
    client_id: Mapped[str] = mapped_column(String(10))
    quantity_sold: Mapped[str] = mapped_column(String(50))

    def __repr__(self) -> str:
        return (f"Transaction(id_vt={self.transaction_id!r}, product_id={self.product_id!r}, date={self.date!r}, "
                f"session_id={self.session_id!r}, client_id={self.client_id!r}, quantity_sold={self.quantity_sold!r})")


def csv_loader() -> None:
    engine = create_engine(f"mysql+pymysql://{username}:{password}@localhost/sales_details", echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    # Drop all existing tables
    Base.metadata.drop_all(engine)
    print("Clean database before loading (useful in this helloworld example)")
    # Create engines
    Base.metadata.create_all(engine)
    with open(cust_csv, newline='', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)
        clients = [Client(client_id=row[0], sex=row[1], birth=row[2]) for row in csvreader]

    try:
        session.bulk_save_objects(clients)
        session.commit()
        print("CSV data inserted into the Clients table successfully.")
    except Exception as e:
        session.rollback()
        print(f"Error inserting data: {e}")
        exit(1)

    with open(products_csv, newline='', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)
        products = [
            Product(product_id=row[0], category=row[1], sub_category=row[2], price=row[3], stock_quantity=row[4]) for
            row in csvreader]
    try:
        session.bulk_save_objects(products)
        session.commit()
        print("CSV data inserted into the Products table successfully.")
    except Exception as e:
        session.rollback()
        print(f"Error inserting data: {e}")
        exit(1)

    with open(transactions_csv, newline='', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)
        transactions = [
            Transaction(product_id=row[0], date=row[1], session_id=row[2], client_id=row[3], quantity_sold=row[4]) for
            row in csvreader]
    try:
        session.bulk_save_objects(transactions)
        session.commit()
        print("CSV data inserted into the Transactions table successfully.")
    except Exception as e:
        session.rollback()
        print(f"Error inserting data: {e}")
        exit(1)
    session.close()


def json_loader() -> None:
    engine = create_engine(f"mysql+pymysql://{username}:{password}@localhost/sales_details", echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    # Drop all existing tables
    Base.metadata.drop_all(engine)
    print("Clean database before loading (useful in this helloworld example)")
    # Create engines
    Base.metadata.create_all(engine)
    with open(cust_json, "r", encoding='utf-8') as file:
        data = json.load(file)
        # list comprehension not working with garbage data
        # clients = [Client(client_id=item['client_id'], sex=item['sex'], birth=item['birth']) for item in data]
        clients = []
        existing_client_id = []
        for item in data:
            if item["client_id"] not in existing_client_id:
                client = Client(client_id=item["client_id"], sex=item['sex'], birth=item['birth'])
                clients.append(client)
                existing_client_id.append(item["client_id"])
    try:
        session.bulk_save_objects(clients)
        session.commit()
        print("Json data inserted into the Clients table successfully.")
    except Exception as e:
        session.rollback()
        print(f"Error inserting data: {e}")
        exit(1)

    with open(products_json, "r", encoding='utf-8') as file:
        data = json.load(file)
        products = []
        existing_product_id = []
        for item in data:
            if item['product_id'] not in existing_product_id:
                product = Product(product_id=item['product_id'], category=item['category'],
                                  sub_category=item['sub_category'],
                                  price=item['price'], stock_quantity=item['stock_quantity'])
                products.append(product)
                existing_product_id.append(item["product_id"])
    try:
        session.bulk_save_objects(products)
        session.commit()
        print("Json data inserted into the Products table successfully.")
    except Exception as e:
        session.rollback()
        print(f"Error inserting data: {e}")
        exit(1)

    with open(transactions_json, "r", encoding='utf-8') as file:
        data = json.load(file)
        transactions = [Transaction(product_id=item['product_id'], date=item["date"], session_id=item['session_id'],
                                    client_id=item['client_id'], quantity_sold=item['quantity_sold']) for item in data]
    try:
        session.bulk_save_objects(transactions)
        session.commit()
        print("json data inserted into the Transactions table successfully.")
    except Exception as e:
        session.rollback()
        print(f"Error inserting data: {e}")
        exit(1)
    session.close()


def json_mongo_loader() -> None:
    with MongoClient(f'mongodb://{usr}:{pwd}@{host}:27017/') as client:
        db = client['sales']
        #we drop existing table (easy solution in testing snippet)
        collections = db.list_collection_names()
        print(collections)
        for collection in collections:
            db.drop_collection(collection)
            print("existing table dropped")
        db = client['sales']
        customers = db["clients"]
        products= db["products"]
        order_detail=db["order_detail"]
        #Assuming given data "ok"
        with open(cust_json, 'r', encoding='utf-8') as file:
            data = json.load(file)
            try:
                customers.insert_many(list(data))
            except Exception as e:
                print(f"Error inserting data: {e}")
                pass
        with open(products_json, 'r', encoding='utf-8') as file:
            data = json.load(file)
            try:
                products.insert_many(list(data))
            except Exception as e:
                print(f"Error inserting data: {e}")
                pass
        with open(transactions_json, 'r', encoding='utf-8') as file:
            data = json.load(file)
            try:
                order_detail.insert_many(list(data))
            except Exception as e:
                print(f"Error inserting data: {e}")
                pass

if __name__ == "__main__":
    aaa = input(
        "Make your choice:\n"
        "1 to load a CSV into an SQL database\n"
        "2 to load a JSON into an SQL database.\n"
        "3 to load a JSON into an MongoDB database.\n"
    )
    try:
        aaa in [1, 2, 3]
    except ValueError:
        print("Please enter a valid choice: number 1, 2 or 3")
        exit(1)
    try:
        load_dotenv()
        username = os.getenv("MYSQL_USER")
        password = os.getenv("MYSQL_ROOT_PASSWORD")
        usr = os.getenv("MONGO_USR")
        pwd = os.getenv("MONGO_PW")
        host= os.getenv("MONGO_HOST")
    except Exception as e:
        print("environment variables not set, or not found")
        exit(1)

    if aaa == "1":
        csv_loader()
        print("csv data inserted into sql tables successfully .")

    if aaa == "2":
        json_loader()
        print("json data inserted into sql tables successfully .")

    if aaa == "3":
        json_mongo_loader()
