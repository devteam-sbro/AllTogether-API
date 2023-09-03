import os
import sys

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from backend import app
from backend.libs.database import db

manager = Manager(app)
migrate = Migrate(app, db, compare_type=True)

manager.add_command('db', MigrateCommand)


@manager.command
def runserver():
    app.run(host='0.0.0.0', port=8080)


if __name__ == "__main__":
    # Set Python Working directory to backend package path
    os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
    manager.run()
