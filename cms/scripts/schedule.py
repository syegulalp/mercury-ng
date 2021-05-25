import sys, os, datetime

sys.path.insert(0, os.getcwd())

from cms.models import Queue, Post, db, db_context
from cms.models.enums import PublicationStatus, QueueStatus
from cms.models.utils import send_email

results = []


def log(*a):
    if isinstance(a, tuple):
        results.append(str(" ".join(a)))
    else:
        results.append(a)
    print(a)


class QueueAlreadyRunning(Exception):
    pass


class QueueInsertInProgress(Exception):
    pass


@db_context
def check_queue_status():
    print("Mercury job runner started.")

    force = False
    if len(sys.argv) > 1 and sys.argv == "--force":
        force = True

    if not force:
        try:
            last_job = Queue.jobs().order_by(Queue.date_inserted.desc()).limit(1).get()
        except Queue.DoesNotExist:
            pass
        else:
            if last_job.date_inserted > datetime.datetime.utcnow() - datetime.timedelta(
                seconds=15
            ):
                log("Queue runner not activated; insert may be in progress.")
                send_email(results)
                raise QueueInsertInProgress()

    cjob = (
        Queue.control_jobs()
        .where(Queue.status << (QueueStatus.RUNNING, QueueStatus.MANUAL))
        .order_by(Queue.date_inserted)
    )
    if cjob.count() > 0:
        top_job: Queue = cjob.get()
        if top_job.date_updated < datetime.datetime.utcnow() - datetime.timedelta(
            minutes=2
        ):
            top_job.status = QueueStatus.WAITING
            top_job.save()
        else:
            print("Queue already running.", file=sys.stderr)
            log("Queue runner not activated; job already in progress.")
            send_email(results)
            raise QueueAlreadyRunning()


@db_context
def poll_for_jobs():
    blogs = set()
    do_email = False

    log("Polling for scheduled jobs.")

    total_posts = 0
    total_jobs = 0

    for scheduled_post in Post.select().where(
        Post.status == PublicationStatus.SCHEDULED,
        Post.date_published <= datetime.datetime.utcnow(),
    ):
        total_posts += 1
        scheduled_post.status = PublicationStatus.PUBLISHED
        scheduled_post.save()
        total_jobs += scheduled_post.enqueue()
        blogs.add(scheduled_post.blog)

    if not blogs:
        log("No scheduled jobs found.")
    else:
        do_email = True
        for x in blogs:
            log(f"Scheduled jobs found in blog: {x.title}")
        log(f"{total_posts} post(s) scheduled.")
        log(f"{total_jobs} jobs(s) scheduled.")

    log("Polling for available jobs in queue.")

    valid_jobs = Queue.select(Queue.blog).where(Queue.status != QueueStatus.FAILED)

    for queue_item in valid_jobs.distinct():
        job_count = valid_jobs.count()
        log(f"{job_count} jobs found for blog {queue_item.blog.title}.")
        do_email = True
        blogs.add(queue_item.blog)

    return blogs, do_email


def run_queue(blogs, do_email):
    for b in blogs:
        try:
            Queue.run_queue_(b)
        except Exception as e:
            do_email = True
            log(f"Failures for queue run on blog {b.title}: {e}")
            job: Queue = Queue.control_jobs().get()
            if job.status == QueueStatus.RUNNING:
                job.status == QueueStatus.WAITING
                job.save()
        else:
            failures = Queue.failures(b).count()
            if failures:
                do_email = True
                log(f"{failures} failures recorded in queue for blog {b.title}.")
                print(
                    "Publishing failure on blog ",
                    b.title,
                    "; see publishing queue",
                    file=sys.stderr,
                )
            else:
                log(f"Jobs finished for blog {b.title}.")

    return do_email


def run_jobs():
    try:
        check_queue_status()
    except (QueueAlreadyRunning, QueueInsertInProgress):
        return
    while True:
        blogs_with_jobs, do_email = poll_for_jobs()
        if not blogs_with_jobs:
            break
        do_email = run_queue(blogs_with_jobs, do_email)
    print("Mercury job runner finished.")
    if do_email:
        send_email(results)


if __name__ == "__main__":
    try:
        run_jobs()
    except Exception as e:
        log(f"Error when running jobs: {e}")
        send_email(results)
