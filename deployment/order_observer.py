import sys
from datetime import datetime, timedelta
from os.path import dirname, abspath

from apscheduler.schedulers.background import BlockingScheduler
from pytz import timezone
from sqlalchemy import and_


sched = BlockingScheduler()


def fail_order(order):
    # from backend.models.order import Order, OrderTxHistory
    # from backend.libs.database import db
    # import backend.libs.notify as notify

    order.proceed_failure(order.orderer)
    # notify.proceed_order(order)


def proceed_order(order):
    from backend.models.order import Order, OrderTxHistory
    from backend.libs.database import db
    import backend.libs.notify as notify

    prev_status = order.order_status
    order.order_status = Order.STATUS_PROCEED
    order.order_modified_at = datetime.now()

    user = order.worker
    tx = OrderTxHistory(order_idx=order.idx, user_idx=user.idx,
                        status_from=prev_status,
                        created_at=datetime.now(timezone('Asia/Seoul')),
                        status_to=Order.STATUS_PROCEED)
    db.session.add(tx)
    notify.proceed_order(None, order)


def done_order(order):
    from backend.models.order import Order, OrderTxHistory
    from backend.libs.database import db
    import backend.libs.notify as notify

    prev_status = order.order_status
    order.order_status = Order.STATUS_DONE
    order.order_modified_at = datetime.now()

    tx = OrderTxHistory(order_idx=order.idx, user_idx=order.worker.idx,
                        status_from=prev_status,
                        created_at=datetime.now(timezone('Asia/Seoul')),
                        status_to=Order.STATUS_PROCEED)
    order.pay_for_done(tx=tx)

    db.session.add(tx)
    notify.done_order(None, order)


def job_proceed_order():
    from backend.models.order import Order
    from backend.libs.database import db
    since = datetime.now() - timedelta(seconds=30)
    with db.session.begin_nested():
        o = Order.query.filter(
            and_(Order.order_modified_at <= since,
                 Order.order_status == Order.STATUS_REGISTERD)).with_for_update().all()
        for order in o:
            proceed_order(order)
        print('[%s] order proceed result : %d' % (datetime.now(), len(o)))
    db.session.commit()


def job_done_order():
    from backend.models.order import Order
    from backend.libs.database import db
    since = datetime.now() - timedelta(days=1)

    with db.session.begin_nested():
        o = Order.query.filter(
            and_(Order.work_date <= since,
                 Order.order_status == Order.STATUS_PROCEED)).with_for_update().all()
        for order in o:
            done_order(order)
        print('[%s] order done result : %d' % (datetime.now(), len(o)))
    db.session.commit()


def job_fail_order():
    from backend.models.order import Order
    from backend.libs.database import db
    since = datetime.now() - timedelta(days=1)

    with db.session.begin_nested():
        o = Order.query.filter(
            and_(Order.work_date <= since,
                 Order.order_status == Order.STATUS_READY)).with_for_update().all()
        for order in o:
            fail_order(order)
        print('[%s] order fail result : %d' % (datetime.now(), len(o)))
    db.session.commit()


def set_pythonpath():
    d = dirname(dirname(abspath(__file__)))
    sys.path.append(d)
    return d


if __name__ == '__main__':
    cur_path = set_pythonpath()
    job_done_order()
    job_fail_order()
    sched.add_job(job_proceed_order, 'interval', minutes=1)
    sched.add_job(job_done_order, 'cron', hour=7, minute=00)
    sched.add_job(job_fail_order, 'cron', hour=7, minute=00)
    sched.start()
