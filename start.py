from os.path import expanduser, exists
from os import makedirs
import argparse
import time
from sqlalchemy import create_engine, and_, or_
from models import Task, Base
from datetime import timedelta, datetime
from sqlalchemy.orm import sessionmaker

home_dir = expanduser('~')
tracker_dir = home_dir + '/easy_tracker'
tracker_db = home_dir + '/easy_tracker/lite.db'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('init', nargs='?')
    parser.add_argument('--category', '-c', help='Task short description')
    parser.add_argument('--task', '-t', help='Task short description')
    parser.add_argument('--days', '-d', help='How many days (optional for reports)')
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
        report(category, task, days)


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


def report(category, task, days):
    if validate_init() is True:
        engine = create_engine("sqlite:///" + tracker_db, echo=False)
        Session = sessionmaker(bind=engine)
        session = Session()

        if category != '' and task != '' and days != 0:
            current_time = datetime.utcnow()
            days_ago = current_time - timedelta(days=int(days))
            n = session.query(Task).filter(and_(Task.category == category, Task.name == task,
                                                Task.start >= int(datetime.timestamp(days_ago)))).all()
            if not n:
                print('Can not find anything with this parameters. Return all.')
                n = session.query(Task).all()
        elif category != '' and task != '' and days == 0:
            n = session.query(Task).filter(and_(Task.category == category, Task.name == task)).all()
            if not n:
                print('Can not find anything with this parameters. Return all.')
                n = session.query(Task).all()
        elif category != '' and task == '' and days != 0:
            current_time = datetime.utcnow()
            days_ago = current_time - timedelta(days=int(days))
            n = session.query(Task).filter(
                and_(Task.category == category, Task.start >= int(datetime.timestamp(days_ago)))).all()
            if not n:
                print('Can not find anything with this parameters. Return all.')
                n = session.query(Task).all()
        elif category == '' and task != '' and days != 0:
            current_time = datetime.utcnow()
            days_ago = current_time - timedelta(days=int(days))
            n = session.query(Task).filter(
                and_(Task.name == task, Task.start >= int(datetime.timestamp(days_ago)))).all()
            if not n:
                print('Can not find anything with this parameters. Return all.')
                n = session.query(Task).all()
        elif category != '' and task == '' and days == 0:
            n = session.query(Task).filter(Task.category == category).all()
            if not n:
                print('Can not find anything with this parameters. Return all.')
                n = session.query(Task).all()
        elif category == '' and task != '' and days == 0:
            n = session.query(Task).filter(Task.name == task).all()
            if not n:
                print('Can not find anything with this parameters. Return all.')
                n = session.query(Task).all()
        elif category == '' and task == '' and days != 0:
            current_time = datetime.utcnow()
            days_ago = current_time - timedelta(days=int(days))
            n = session.query(Task).filter(Task.start >= int(datetime.timestamp(days_ago))).all()
            if not n:
                print('Can not find anything with this parameters. Return all.')
                n = session.query(Task).all()
        else:
            n = session.query(Task).all()

        total = timedelta(seconds=0)
        template = "{0:2}|{1:15}|{2:65}|{3:15}|"
        print(template.format('Id', 'Category', 'Name', 'Spent hours'))
        for i in n:
            diff = (i.stop - i.start)
            td = timedelta(seconds=diff)
            total = total + td
            print(template.format(i.id, i.category, i.name, str(td)))
        print('*****************')
        print('Total: %s (hh:mm:ss)' % total)


def validate_init():
    if not exists(tracker_db):
        print('Seems like you use this tracker first time. Please use "init" command first')
        return False
    else:
        return True

if __name__ == '__main__':
    main()
