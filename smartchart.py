import matplotlib.pyplot as plt
import numpy as np
from pandas import date_range, Series, DataFrame, read_csv, qcut, merge, concat, TimeGrouper, to_datetime, DatetimeIndex, read_sql
from sqlalchemy import create_engine
from models import Task, Base
from sqlalchemy.orm import sessionmaker
from start import tracker_db


def graf():
    engine = create_engine("sqlite:///" + tracker_db, echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()
    """
    Better pull it to csv i think
    """
    q = session.query(Task)
    # do some efl
    # read data into pandas directly from the query `q`
    df = read_sql(q.statement, q.session.bind)

    # pivot the results
    df_pivot = df.pivot(index="id", columns="name", values="name")
    print(df_pivot)
    # df.plot(kind='bar')
    # plt.show()

