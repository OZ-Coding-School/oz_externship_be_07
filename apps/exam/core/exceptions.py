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


class CodeMismatchError(Exception):
    pass


"""Admin Deployment Domain"""


class AdminDeploymentNotFoundError(Exception):
    pass


class AdminDeploymentTargetNotFoundError(Exception):
    pass


class AdminDeploymentDuplicateError(Exception):
    pass


class AdminDeploymentConflictError(Exception):
    pass
