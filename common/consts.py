from common.models import Permission
from common.models import Role

ROLES_PERMISSIONS = {
    Role.STAFF: (Permission.VIEW_USERS, Permission.CHANGE_ROLES),
}
