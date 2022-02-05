########
#  Exceptions which can be raised in AMAS
########


class UniqueNameError(LookupError):
    """ Raised when encountering non-unique entry conditions. For example, versions in a channel should be uniquely named. """
    pass


class ModelNotFound(LookupError):
    """ Raised when we are looking for a model by name which we expect to find but do not find it """
    pass


class InsufficientApplicationInformation(ValueError):
    """ Raised when generating an iOS download package and required information is missing """
    pass


class InvalidAdministrator(ValueError):
    """ Raised when the user is attempting an operation on an application they do not own """
    pass


class UpdateError(ValueError):
    """ Raised when a data update operation failed to succeed """
    pass


class ResourceNotFound(Exception):
    """ Raised if a resource does not exist """
    pass


class ResourceExists(Exception):
    """ Raised if a resource does already exist and cannot be overwritten """
    pass
