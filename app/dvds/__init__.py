from flask import Blueprint

dvds = Blueprint('dvds', __name__, url_prefix='/dvds')

# This must be imported after the Blueprint definition as the
# definition is imported into the app creation call and then
# the following import registers all the routes found under this
# blueprint.
from . import routes  # noqa: E402,F401
