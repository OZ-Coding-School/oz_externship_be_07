"""normal"""


class DeploymentNotFoundError(Exception):
    pass


class DeploymentForbiddenError(Exception):
    pass


class DeploymentInvalidSessionError(Exception):
    pass


class DeploymentGoneError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class DeploymentLockedError(Exception):
    pass


""" access """


class CodeMismatchError(Exception):
    pass


class AccessDeploymentNotFoundError(Exception):
    pass


class AccessDeploymentForbiddenError(Exception):
    pass


class AccessDeploymentLockedError(Exception):
    pass


class AccessUserNotFoundError(Exception):
    pass


class AccessCodeMismatchError(Exception):
    pass
