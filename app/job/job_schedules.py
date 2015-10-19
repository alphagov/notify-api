from apscheduler.schedulers.blocking import BlockingScheduler
from sms_jobs import send_sms

sched = BlockingScheduler()


@sched.scheduled_job('interval', minutes=1)
def send_sms_schedule():
    print("Sending")
    sched.add_job(func=send_sms, max_instances=1, id="sms_sending_job")


sched.start()
