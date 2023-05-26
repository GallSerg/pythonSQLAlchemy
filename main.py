import dbapi
import json
import os
import sqlalchemy as sq
from sqlalchemy.orm import sessionmaker

if __name__ == "__main__":
    # Connect to database (Task 1)
    host = os.getenv('NET_ALCH_HOST')
    port = os.getenv('NET_ALCH_PORT')
    login = os.getenv('NET_ALCH_LOGIN')
    password = os.getenv('NET_ALCH_PASSWORD')
    db_name = os.getenv('NET_ALCH_DB_NAME')
    DSN = f"postgresql://{login}:{password}@{host}:{port}/{db_name}"
    engine = sq.create_engine(DSN)
    dbapi.create_tables(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Load data from json (Task 3)
    with open('fixtures/tests_data.json', 'r') as fd:
        data = json.load(fd)
    model = dict(publisher=dbapi.Publisher, shop=dbapi.Shop, book=dbapi.Book, stock=dbapi.Stock, sale=dbapi.Sale)

    # Fill database from json data (Task 3)
    for record in data:
        temp = model[record['model']]
        session.add(temp(id=record.get('pk'), **record.get('fields')))
    session.commit()

    # Select books (Task 2)
    q = session.query(dbapi.Publisher)
    publishers = q.all()
    print('Publishers and their ids in database:', ', '.join([p.name+'-'+str(p.id) for p in publishers]))
    publishers = {p.id: p.name for p in publishers}
    author = input('Input one of below publishers (name or id): ')
    if author not in publishers.values():
        author = publishers[int(author)]
    q = session.query(dbapi.Book.title, dbapi.Shop.name, dbapi.Sale.price, dbapi.Sale.count, dbapi.Sale.date_sale).\
        join(dbapi.Publisher).join(dbapi.Stock).join(dbapi.Shop).join(dbapi.Sale).\
        filter(dbapi.Publisher.name == author)
    # print(q)
    for title, shop, price, count, date in q.all():
        print(f"{title: <40} | {shop: <10} | {int(price*count): <4} | {date.strftime('%d-%m-%Y')}")
