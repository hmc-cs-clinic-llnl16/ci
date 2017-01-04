import os as _os
_basedir = _os.path.abspath(_os.path.dirname(__file__))

static_url_path = '/static'
static_folder = 'static'

SECRET_KEY = 'SUPER SECRET'

WTF_CSRF_ENABLED = True

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + _os.path.join(_basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = _os.path.join(_basedir, 'db_repository')
