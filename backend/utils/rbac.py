from fastapi import Depends, HTTPException, status
from model.users import User
from utils.auth_utils import get_current_user

ADMIN_ROLES = {
    "municipal_officer",
    "department_head",
    "city_planner",
    "system_admin",
}


def require_roles(*allowed_roles: str):
    """
    Dependency factory for role-based access checks.
    Returns current user if role is allowed, otherwise raises 403.
    """
    normalized = {role.strip().lower() for role in allowed_roles}

    def _role_guard(current_user: User = Depends(get_current_user)) -> User:
        user_role = (current_user.role or "citizen").strip().lower()
        if user_role not in normalized:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions for this resource",
            )
        return current_user

    return _role_guard
