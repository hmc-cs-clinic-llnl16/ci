import multiprocessing
import subprocess
import datetime

from app import app, db, models


process = None
queue = multiprocessing.Queue()

def process_queue(q):
    while True:
        task_id = q.get()
        task = models.Task.query.get(task_id)
        print task

        # Do something with the task
        q.task_done()

def enqueue_task(data):
    task = models.Task(
        application=data['application'], tag=data.get('tag', 'master'),
        compiler=data['compiler'], num_trials=data['num_trials'],
        problem_size=data['size'], status='Queued', complete=False,
        timestamp=datetime.datetime.now()
    )
    db.session.add(task)
    db.session.commit()
    queue.put_nowait(task.id)
    return task.id

@app.before_first_request
def start_first_request():
    global process
    process = multiprocessing.Process(target=process_queue, args=(queue,))
    process.start()
