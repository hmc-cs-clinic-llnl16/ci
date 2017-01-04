from app import app, db, models, worker

from flask import render_template, redirect, flash, url_for
from flask_wtf import FlaskForm
from wtforms import SelectField
from urllib import quote_plus

valid_applications = []

@app.before_first_request
def get_valid_applications():
    global valid_applications
    valid_applications = [(application.id, quote_plus(application.id)) for application in models.Application.query.all()]

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', valid_applications=valid_applications)

@app.route('/webhook/<repository>', methods=['POST'])
def repository_webhook(repository):
    return "TEST, {}".format(repository)

def template_variables_for(application):
    for app, url in valid_applications:
        if url == application:
            application = app
            break
    else:
        flash('Unknown application {}.'.format(application))
        return 'index.html', None, None

    class RegressionForm(FlaskForm):
        compiler = SelectField(
            'Compiler', choices=[(compiler.id, compiler.id) for compiler in models.Compiler.query.all()]
        )
        num_trials = SelectField(
            'Number of Trials', choices=[('1', '1'), ('5', '5'), ('10', '10'), ('20', '20')]
        )
        size = SelectField(
            'Problem Size', choices=[('100', '100'), ('1000', '1000'), ('10000', '10000')]
        )

    repo_id = models.Application.query.get(application).repo_id
    repo = models.Repository.query.get(repo_id)
    url = repo.url

    return ('run_regression.html', RegressionForm(), {
        'app_name': application, 'app_url': url,
        'title': 'Run Regression for {}'.format(application)
    })

@app.route('/regression/<application>', methods=['GET', 'POST'])
def run_regression(application):
    template, form, variables = template_variables_for(application)
    if not form:
        return redirect(url_for('index'))
    if form.validate_on_submit():
        data = form.data
        data.update({'application': application})
        task_id = worker.enqueue_task(data)
        return redirect(url_for('regression_status', task_id=task_id))
    return render_template(template, form=form, getattr=getattr, valid_applications=valid_applications, **variables)

@app.route('/regression_status/<int:task_id>')
def regression_status(task_id):
    task = models.Task.query.get(task_id)
    return render_template("task_status.html", task=task, valid_applications=valid_applications)

@app.route('/tasklist')
def tasklist():
    return render_template("tasklist.html", tasks=models.Task.query.all(), valid_applications=valid_applications)
