from app import db, app

import os
import json

class DebugModel(object):
    def __str__(self):
        return repr(self)

    def __unicode__(self):
        return unicode(str(self))

    def __repr__(self):
        return json.dumps({key: str(value) for key, value in vars(self).iteritems()}, sort_keys=True, indent=4, separators=(',', ': '))

class Task(db.Model, DebugModel):
    id = db.Column(db.Integer, primary_key=True)
    application = db.Column(db.String(30), db.ForeignKey('application.id'))
    tag = db.Column(db.String(64))
    compiler = db.Column(db.String(12), db.ForeignKey('compiler.id'))
    num_trials = db.Column(db.Integer)
    problem_size = db.Column(db.Integer)
    status = db.Column(db.String(10))
    complete = db.Column(db.Boolean)
    timestamp = db.Column(db.DateTime)

    def __str__(self):
        return "Task {} on {} for {}".format(self.id, self.compiler, self.tag)

class Compiler(db.Model, DebugModel):
    id = db.Column(db.String(12), primary_key=True)

    def __str__(self):
        return str(self.id)

class Build(db.Model, DebugModel):
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.String(30), db.ForeignKey('application.id'))
    repository_id = db.Column(db.String(30), db.ForeignKey('repository.id'))
    compiler_id = db.Column(db.String(12), db.ForeignKey('compiler.id'))
    clone_command = db.Column(db.String(1000))
    build_command = db.Column(db.String(1000))

    def __str__(self):
        return "Build {} for {}".format(self.id, self.application_id)

class Application(db.Model, DebugModel):
    id = db.Column(db.String(30), primary_key=True)
    repo_id = db.Column(db.String(30), db.ForeignKey('repository.id'))
    path = db.Column(db.String(100))

    def __str__(self):
        return str(self.id)

class Repository(db.Model, DebugModel):
    id = db.Column(db.String(30), primary_key=True)
    url = db.Column(db.String(200))
    git = db.Column(db.Boolean)
    applications = db.relationship('Application', backref='repository', lazy='dynamic')

    def __str__(self):
        return str(self.id)

@app.before_first_request
def init_database():
    here = os.path.dirname(os.path.abspath(__file__))
    for table, class_ in [('compilers', Compiler), ('repositories', Repository), ('applications', Application), ('builds', Build)]:
        table_json_path = os.path.join(here, 'config', '{}.json'.format(table))
        with open(table_json_path) as table_json:
            json_data = json.load(table_json)

        for entry in json_data:
            row = class_(**entry)
            try:
                found = class_.query.get(row.id)
            except TypeError as e:
                # Sometimes there is a call to len() on a NoneType if empty
                db.session.add(row)
                db.session.commit()
            else:
                # Sometimes it just returns None
                if found is None:
                    db.session.add(row)
                    db.session.commit()
