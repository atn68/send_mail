import sys
import os
import csv
import json
import redis
import rq
import time
from rq.job import Job, JobStatus
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from template import MailTemplate
from engine.export_file import run as run_task


redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')

conn = redis.from_url(redis_url)

queue = rq.Queue(connection=conn)


def validate_filepath(file_path):
    if not (file_path and os.path.isfile(file_path)):
        raise Exception(f'Invalid file path {file_path}')


def load_recipients(file_path):
    validate_filepath(file_path)
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row


def load_template(file_path):
    validate_filepath(file_path)
    with open(file_path, 'r') as f:
        return json.loads(f.read())


def generate_content(template, data):
    mail_template = MailTemplate(template, data)
    return mail_template.render()


def write_error_recipients(recipients=[]):
    if not recipients:
        return
    with open('errors.csv', 'w+') as f:
        writer = csv.DictWriter(
            f, fieldnames=recipients[0].keys())
        writer.writeheader()
        writer.writerows(recipients)


def job_status_acknowledge(jobs=[]):
    round = 0
    while any(jobs):
        print(f'Check round: {round + 1}')
        print(f'Remain jobs: {len(jobs)}')
        jobs = list(filter(
            lambda job: not (job.is_finished or job.is_failed or job.is_stopped or job.is_canceled), jobs))
        # Exponential backoff in millisecond
        time.sleep((len(jobs)/(2**round)) / 1000)
        round += 1


def process(argv=[]):
    if (len(argv) != 2):
        raise Exception('Illegal arguments')

    template = load_template(argv[0])
    jobs = []
    error_recipients = []

    start_time = time.time()
    for recipient in load_recipients(argv[1]):
        if not recipient['EMAIL']:
            error_recipients.append(recipient)
            continue

        content = generate_content(template=template['body'], data=dict(
            **recipient, TODAY=datetime.now().strftime('%d %b %y')))
        job = queue.enqueue(run_task, args=(dict(
            template, to=recipient['EMAIL'], body=content),))
        jobs.append(job)

    print('Push %d jobs in %.2fs' % (len(jobs), time.time() - start_time,))
    job_status_acknowledge(jobs)
    print('Total time: %.2fs' % (time.time() - start_time,))
    write_error_recipients(error_recipients)
    print('Done')


if __name__ == '__main__':
    process(sys.argv[1:])
