from flask import Blueprint
from flask_restplus import Api

from api.qr_api import api as qr_namespace
from api.login_api import api as login_namespace
app_api = Blueprint('app_api', __name__,url_prefix='/pingan/api')
api1 = Api(app_api,
    title='API',
    version='1.0',
    description='API文档',
    doc='/doc/'
    # All API metadatas
)


api1.add_namespace(qr_namespace)
api1.add_namespace(login_namespace)