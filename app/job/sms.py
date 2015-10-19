from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()


@sched.scheduled_job('interval', minutes=5)
def timed_job():
    print('This job is run every five minutes.')


sched.start()
