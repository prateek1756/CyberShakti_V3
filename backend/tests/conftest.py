import uuid
from datetime import datetime, timezone
from typing import Any, AsyncGenerator, List, Optional

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.sql.visitors import traverse

from app.config import settings
from app.main import app
from app.shared.database import get_db
from app.shared.models import (
    AuditLog,
    BackupCode,
    EmailVerificationToken,
    PasswordResetToken,
    RefreshToken,
    SafetyTip,
    ScanResult,
    ScamAlert,
    TOTPSecret,
    User,
)
from app.shared.security import create_access_token, hash_password

settings.RATE_LIMIT_ENABLED = False

TEST_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
TEST_USER_EMAIL = "user@example.com"
TEST_USER_PASSWORD = "longenough"


class _FakeResult:
    def __init__(self, items: Optional[List[Any]] = None):
        self._items = items or []

    def scalar_one_or_none(self):
        return self._items[0] if self._items else None

    def scalars(self):
        return self

    def all(self):
        return list(self._items)


class FakeStore:
    def __init__(self):
        self.reset()

    def reset(self):
        self.users = {}
        self.refresh = []
        self.totp = []
        self.backup = []
        self.email_tokens = []
        self.reset_tokens = []
        self.scans = []
        self.alerts = []
        self.tips = []
        self.audit = []


STORE = FakeStore()


def _entity(stmt):
    try:
        return stmt.column_descriptions[0].get("entity")
    except Exception:
        return None


def _filters(stmt) -> dict:
    found = {}
    where = getattr(stmt, "whereclause", None)
    if where is None:
        return found

    def visit_binary(bin_):
        left = bin_.left
        right = bin_.right
        name = getattr(left, "key", None)
        if name is None:
            name = getattr(right, "key", None)
            value_side = left
        else:
            value_side = right
        value = getattr(value_side, "value", None)
        if value is None:
            value = getattr(value_side, "effective_value", None)
        found[name] = value

    def visit_unary(un_):
        elem = getattr(un_, "element", None)
        name = getattr(elem, "key", None)
        if name:
            found[name] = None

    traverse(where, {}, {"binary": visit_binary, "unary": visit_unary})
    return found


def _match(obj, filters: dict) -> bool:
    for key, expected in filters.items():
        if key is None:
            continue
        actual = getattr(obj, key, None)
        if expected is None:
            if actual is not None:
                return False
        elif actual != expected:
            return False
    return True


def _statement_params(stmt) -> dict:
    try:
        return dict(stmt.compile().params)
    except Exception:
        return {}


class FakeSession:
    def add(self, obj):
        if getattr(obj, "id", None) is None:
            obj.id = uuid.uuid4()
        if getattr(obj, "created_at", None) is None and hasattr(type(obj), "created_at"):
            try:
                obj.created_at = datetime.now(timezone.utc)
            except Exception:
                pass
        if isinstance(obj, User):
            STORE.users[obj.id] = obj
        elif isinstance(obj, RefreshToken):
            STORE.refresh.append(obj)
        elif isinstance(obj, TOTPSecret):
            STORE.totp.append(obj)
        elif isinstance(obj, BackupCode):
            STORE.backup.append(obj)
        elif isinstance(obj, EmailVerificationToken):
            STORE.email_tokens.append(obj)
        elif isinstance(obj, PasswordResetToken):
            STORE.reset_tokens.append(obj)
        elif isinstance(obj, ScanResult):
            STORE.scans.append(obj)
        elif isinstance(obj, AuditLog):
            STORE.audit.append(obj)
        elif isinstance(obj, ScamAlert):
            STORE.alerts.append(obj)
        elif isinstance(obj, SafetyTip):
            STORE.tips.append(obj)

    async def execute(self, stmt, *args, **kwargs):
        kind = type(stmt).__name__
        if kind == "Delete":
            STORE.backup = []
            return _FakeResult([])

        entity = _entity(stmt)
        params = _statement_params(stmt)
        values = list(params.values())

        def _by_id(collection):
            uid = next((v for v in values if isinstance(v, uuid.UUID)), None)
            if uid is None:
                return []
            if isinstance(collection, dict):
                item = collection.get(uid)
                return [item] if item else []
            return [item for item in collection if getattr(item, "id", None) == uid or getattr(item, "user_id", None) == uid]

        if entity is User:
            uid = next((v for v in values if isinstance(v, uuid.UUID)), None)
            email = next((v for v in values if isinstance(v, str) and "@" in v), None)
            if uid is not None:
                user = STORE.users.get(uid)
                return _FakeResult([user] if user and user.is_active else [])
            if email:
                matches = [u for u in STORE.users.values() if u.email == str(email).lower()]
                return _FakeResult(matches)
            return _FakeResult([])
        if entity is RefreshToken:
            token_hash = next((v for v in values if isinstance(v, str) and len(v) == 64), None)
            items = [t for t in STORE.refresh if token_hash and t.token_hash == token_hash]
            if not items:
                items = _by_id(STORE.refresh)
            return _FakeResult(items)
        if entity is TOTPSecret:
            items = [t for t in STORE.totp if getattr(t, "user_id", None) in values or t in STORE.totp and any(getattr(t, "user_id", None) == v for v in values)]
            return _FakeResult(items)
        if entity is BackupCode:
            return _FakeResult([t for t in STORE.backup if t.user_id in values])
        if entity is EmailVerificationToken:
            token_hash = next((v for v in values if isinstance(v, str) and len(v) >= 32), None)
            return _FakeResult([t for t in STORE.email_tokens if t.token_hash == token_hash])
        if entity is PasswordResetToken:
            token_hash = next((v for v in values if isinstance(v, str) and len(v) >= 32), None)
            return _FakeResult([t for t in STORE.reset_tokens if t.token_hash == token_hash])
        if entity is ScanResult:
            uid = next((v for v in values if isinstance(v, uuid.UUID)), None)
            items = [t for t in STORE.scans if uid is None or t.user_id == uid]
            return _FakeResult(items)
        if entity is ScamAlert:
            return _FakeResult(list(STORE.alerts))
        if entity is SafetyTip:
            return _FakeResult(list(STORE.tips))
        return _FakeResult([])

    async def commit(self):
        return None

    async def flush(self):
        return None

    async def refresh(self, obj):
        return None

    async def rollback(self):
        return None

    async def close(self):
        return None


async def _override_get_db() -> AsyncGenerator[FakeSession, None]:
    if TEST_USER_ID not in STORE.users:
        seed_verified_user()
    yield FakeSession()


app.dependency_overrides[get_db] = _override_get_db


def auth_headers(user_id: uuid.UUID = TEST_USER_ID) -> dict:
    token = create_access_token({"sub": str(user_id), "role": "user"})
    return {"Authorization": f"Bearer {token}"}


def seed_verified_user() -> User:
    user = User(
        id=TEST_USER_ID,
        email=TEST_USER_EMAIL,
        password_hash=hash_password(TEST_USER_PASSWORD),
        email_verified=True,
        is_active=True,
        role="user",
        totp_enabled=False,
        created_at=datetime.now(timezone.utc),
    )
    STORE.users[user.id] = user
    return user


@pytest.fixture(autouse=True)
async def _reset_store():
    STORE.reset()
    seed_verified_user()
    yield
    STORE.reset()


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
