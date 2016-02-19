from os.path import expanduser, exists
from os import makedirs
import argparse
import time
from sqlalchemy import create_engine, and_
from models import Task, Base
from datetime import timedelta, datetime
from sqlalchemy.orm import sessionmaker
import re
import smartchart

home_dir = expanduser('~')
tracker_dir = home_dir + '/easy_tracker'
tracker_db = home_dir + '/easy_tracker/lite.db'


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('init', nargs='?', help="Can be init, start, stop, report, add-time, charts")
    parser.add_argument('--category', '-c', help='Category like JIRA or Work or Private etc.')
    parser.add_argument('--task', '-t', help='Task short description')
    parser.add_argument('--days', '-d', help='How many days (optional for reports)')
    parser.add_argument('--date_from', '-f', help='Start date. Format should be: dd-mm-yyyy')
    parser.add_argument('--time_spent', '-s', help='Time spent. Format: XhYm')
    parser.add_argument('--task_id', '-i', help='Id of task which need remove')

    """
    Need add remove (by id)
    Add statistic (pandas etc.)
    """
    namespace = parser.parse_args()

    if namespace.init == 'start':
        if namespace.task is None or namespace.category is None:
            print('Please add category and task. Use start --category="Your category" --task="Your task"')
        else:
            start(namespace.category, namespace.task)
    if namespace.init == 'init':
        init_tracker()

    if namespace.init == 'stop':
        stop()

    if namespace.init == 'add-time':
        if namespace.task is None or namespace.category is None or namespace.date_from is None \
                or namespace.time_spent is None:
            print('Missed some required arguments. Use --help for details')
        else:
            add_time(namespace.date_from, namespace.time_spent, namespace.category, namespace.task)

    if namespace.init == 'report':
        category = ''
        task = ''
        days = 0
        if namespace.category:
            category = namespace.category
        if namespace.task:
            task = namespace.task
        if namespace.days:
            days = namespace.days
        report(**{'category': category, 'days': days, 'task': task})

    if namespace.init == 'remove':
        if namespace.task_id is None:
            print('Do you know task ID which need remove? Try get report for additional information')
        else:
            remove_log(namespace.task_id)

    if namespace.init == 'graf':
        smartchart.graf()


def init_tracker():
    if not exists(tracker_dir):
        makedirs(tracker_dir)

    engine = create_engine("sqlite:///" + tracker_db, echo=False)
    Base.metadata.create_all(engine)
    print('Created new database in %s. Run tracker with --help option for more information' % tracker_db)


def start(category, issue):
    if validate_init() is True:
        now = int(time.time())
        engine = create_engine("sqlite:///" + tracker_db, echo=False)
        Session = sessionmaker(bind=engine)
        session = Session()

        n = session.query(Task).order_by(Task.id.desc()).first()
        if n is not None:
            if n.start == n.stop:
                print("Please stop last task first. Use stop command")
            else:
                task = Task(category, issue, now, now)
                session.add(task)
                session.commit()
                session.close()
                print('You working on task: %s ' % issue)
        else:
            task = Task(category, issue, now, now)
            session.add(task)
            session.commit()
            session.close()
            print('You working on task: %s ' % issue)


def stop():
    if validate_init() is True:
        now = int(time.time())
        engine = create_engine("sqlite:///" + tracker_db, echo=False)
        Session = sessionmaker(bind=engine)
        session = Session()

        n = session.query(Task).order_by(Task.id.desc()).first()
        session.query(Task).filter(Task.id == n.id).update({'stop': now})
        print(n.name + " stopped!")
        session.commit()
        session.close()


def remove_log(task_id):
    if validate_init() is True:
        engine = create_engine("sqlite:///" + tracker_db, echo=False)
        Session = sessionmaker(bind=engine)
        session = Session()
        n = session.query(Task)
        n.filter(Task.id == task_id).delete()
        session.commit()
        session.close()


def report(**kwargs):

    if validate_init() is True:
        engine = create_engine("sqlite:///" + tracker_db, echo=False)
        Session = sessionmaker(bind=engine)
        session = Session()

        n = session.query(Task)
        for key in kwargs:
            current_time = datetime.utcnow()
            if key == 'days' and kwargs[key] != '':
                days_ago = current_time - timedelta(days=int(kwargs[key]))
                n = n.filter(and_(Task.start >= int(datetime.timestamp(days_ago))))
            if key == 'category' and kwargs[key] != '':
                n = n.filter(and_(Task.category == kwargs[key]))
            if key == 'task' and kwargs[key] != '':
                n = n.filter(and_(Task.name == kwargs[key]))
            n.all()

        if not n:
            print('Can not find anything with this parameters. Return all.')
            n = session.query(Task).all()

        total = timedelta(seconds=0)
        template = "{0:2}|{1:15}|{2:65}|{3:15}|{4:20}|"
        print(template.format('Id', 'Category', 'Name', 'Spent hours', 'Date'))
        for i in n:
            diff = (i.stop - i.start)
            td = timedelta(seconds=diff)
            total = total + td
            d = datetime.fromtimestamp(i.start)
            print(template.format(i.id, i.category, i.name, str(td), str(d)))
        print('*****************')
        print('Total: %s (hh:mm:ss)' % total)


def add_time(date_from, time_spent, category, issue):
    if validate_init() is True:
        engine = create_engine("sqlite:///" + tracker_db, echo=False)
        Session = sessionmaker(bind=engine)
        session = Session()
        now = int(time.time())
        try:
            dt = int(time.mktime(datetime.strptime(date_from, "%d-%m-%Y").timetuple()))
            if dt >= now:
                print('Date should be in past.')
                return False
        except ValueError:
            print('Wrong date format. Use --help for additional information')
            return False

        try:
            result = re.search('(.*)h', time_spent)
            hours = result.group(1)
        except AttributeError:
            hours = 0

        try:
            result = re.search('h(.*)m', time_spent)
            minutes = result.group(1)
        except AttributeError:
            minutes = 0

        delta_minutes = int(hours) * 60 + int(minutes)

        stop_date = dt + delta_minutes * 60

        task = Task(category, issue, dt, stop_date)
        session.add(task)
        session.commit()
        session.close()
        print('You added time for task: %s ' % issue)


def validate_init():
    if not exists(tracker_db):
        print('Seems like you use this tracker first time. Please use "init" command first')
        return False
    else:
        return True

if __name__ == '__main__':
    main()
