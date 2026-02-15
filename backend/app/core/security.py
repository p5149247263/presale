from dataclasses import dataclass
from fastapi import Header, HTTPException


@dataclass
class UserContext:
    user_id: str
    role: str


ROLE_PERMISSIONS = {
    "admin": {"read", "write", "approve", "export"},
    "presales": {"read", "write", "approve", "export"},
    "reviewer": {"read", "approve"},
    "viewer": {"read"},
}


def get_user_context(
    x_user_id: str = Header(default="demo-user"),
    x_role: str = Header(default="presales"),
) -> UserContext:
    if x_role not in ROLE_PERMISSIONS:
        raise HTTPException(status_code=403, detail="Invalid role")
    return UserContext(user_id=x_user_id, role=x_role)


def ensure_permission(ctx: UserContext, permission: str) -> None:
    if permission not in ROLE_PERMISSIONS.get(ctx.role, set()):
        raise HTTPException(status_code=403, detail=f"Role '{ctx.role}' lacks '{permission}' permission")
