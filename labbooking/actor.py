from dataclasses import dataclass
from flask_login import UserMixin
from .errors import Forbidden


@dataclass(frozen=True)
class Actor(UserMixin):
    id: int
    role: str

    def require(self, *roles):
        if self.role not in roles:
            raise Forbidden("当前账号无权执行此操作。")
