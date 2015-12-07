from apscheduler.schedulers.blocking import BlockingScheduler
from app.job.sms_jobs import send_sms, fetch_sms_status
from app.job.email_jobs import send_email, fetch_email_status

sched = BlockingScheduler()


@sched.scheduled_job('interval', seconds=10)
def send_sms_schedule():
    print("Running sending job Sending")
    sched.add_job(func=send_sms, max_instances=1, id="sms_sending_job")


@sched.scheduled_job('interval', minutes=5)
def send_sms_schedule():
    print("Running status job")
    sched.add_job(func=fetch_sms_status, max_instances=1, id="sms_status_checking_job")


@sched.scheduled_job('interval', seconds=10)
def send_email_schedule():
    print("Running sending job Sending email")
    sched.add_job(func=send_email, max_instances=1, id="email_sending_job")


# @sched.scheduled_job('interval', minutes=1)
# def send_email_schedule():
#     print("Running status job")
#     sched.add_job(func=fetch_email_status, max_instances=1, id="email_status_checking_job")


sched.start()
