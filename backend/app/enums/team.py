from enum import Enum


class MembershipRole(str, Enum):
    MEMBER = "MEMBER"
    ADMIN = "ADMIN"