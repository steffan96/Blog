
from app import create_app, db
import os
import sys
import click



app = create_app()

if __name__ == "__main__":
    app.run(debug=True)

@app.cli.command()
@click.option('--coverage/--no-coverage', default=False,
help='Run tests under code coverage.')
def test(coverage):
    """Run the unit tests."""
    import coverage
    import unittest
    COV = coverage.coverage(branch=True, include='blogproject/*')
    COV.start()
    tests = unittest.TestLoader().discover('.')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()

from flask_migrate import upgrade
from app.models import Role, User

@app.cli.command()
def deploy():
    """"Run deployment tasks."""
    upgrade()
    #create or update user roles
    Role.insert_roles()
    