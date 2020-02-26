#!/opt/applications/env/bin/python
import os
import logging
import time
from apscheduler.schedulers.background import BlockingScheduler, BackgroundScheduler
from apscheduler.triggers.combining import OrTrigger
from apscheduler.triggers.cron import CronTrigger
# from schedular_corn.main import main



import requests

def main():
    print("GOING TO SEND NOTIFICATION")
    response = requests.get("http://0.0.0.0:28100/send_all_notifications")
    # response = requests.get("https://www.digitalocean.com/docs/accounts/security/certificates/")
    # print(response)



logging.basicConfig(filename='scheduler.log',
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S')
logging.getLogger('apscheduler').setLevel(logging.DEBUG)
# scheduler = BackgroundScheduler({'apscheduler.timezone': 'America/Argentina/Buenos_Aires'})



trigger = OrTrigger([
   CronTrigger(hour='03', minute='29', second='29', timezone='America/Argentina/Buenos_Aires'),
   CronTrigger(hour='11', minute='29-59', second='9,19,29,39,49,59', timezone='America/Argentina/Buenos_Aires'),
   CronTrigger(hour='12', minute='0-15', second='9,19,29,39,49,59', timezone='America/Argentina/Buenos_Aires'),
   CronTrigger(hour='14', minute='0-59', second='9,19,29,39,49,59', timezone='America/Argentina/Buenos_Aires'),
   CronTrigger(hour='15', minute='0-15', second='9,19,29,39,49,59', timezone='America/Argentina/Buenos_Aires'),
   CronTrigger(hour='16', minute='14-15', second='9,19', timezone='America/Argentina/Buenos_Aires'),
   CronTrigger(hour='17', minute='29-59', second='9,19,29,39,49,59', timezone='America/Argentina/Buenos_Aires'),
   CronTrigger(hour='18', minute='0-30', second='9,19,29,39,49,59', timezone='America/Argentina/Buenos_Aires'),
   CronTrigger(hour='21', minute='0-59', second='9,19,29,39,49,59', timezone='America/Argentina/Buenos_Aires'),
   CronTrigger(hour='22', minute='0-59', second='9,19,29,39,49,59', timezone='America/Argentina/Buenos_Aires'),
   CronTrigger(hour='23', minute='50', second='59', timezone='America/Argentina/Buenos_Aires'),

])
job_defaults = {
    'coalesce': False,
    'max_instances': 3
}

if __name__ == '__main__':
    scheduler = BackgroundScheduler(timezone='America/Argentina/Buenos_Aires', job_defaults=job_defaults)
    scheduler.add_job(main, trigger)
    scheduler.start()
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    try:
        # This is here to simulate application activity (which keeps the main thread alive).
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        scheduler.shutdown()
