__author__ = 'koba'
from apscheduler.schedulers.blocking import BlockingScheduler

from src.utils import run
from src.spiders import AvitoSpider, IRRSpider
from src.config import JOB_INTERVALS
sched = BlockingScheduler()


@sched.scheduled_job('cron', **JOB_INTERVALS)
def run_spiders():
    bots = (
        (AvitoSpider, {'thread_number': 2}),
        (IRRSpider, {'thread_number': 2}),
    )
    run(bots, debug=True)


if __name__ == '__main__':
    sched.start()

