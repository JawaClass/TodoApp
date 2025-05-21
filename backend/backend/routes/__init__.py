from . import authentication
from . import api


routers = [authentication.router, api.router]
