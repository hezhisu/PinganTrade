from flask import request
from flask_cors import CORS
from flask_script import Manager, Shell

__author__ = 'hezhisu'
import os
from app import create_app

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
# manager.add_command('db', MigrateCommand)

CORS(app)
if __name__ == '__main__':
    # app.run(debug=True,host='0.0.0.0')
    app.run(debug=True)