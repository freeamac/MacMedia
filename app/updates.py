###########
# Handle updates of data objects in the model
###########

from datetime import datetime
import os

from app.exceptions import InvalidAdministrator, ModelNotFound, UniqueNameError, UpdateError, ResourceNotFound
from app.models import DVDs