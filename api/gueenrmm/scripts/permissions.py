from rest_framework import permissions

from gueenrmm.permissions import _has_perm


class ScriptsPerms(permissions.BasePermission):
    def has_permission(self, r, view):
        if r.method == "GET":
            return _has_perm(r, "can_list_scripts")
        else:
            return _has_perm(r, "can_manage_scripts")
