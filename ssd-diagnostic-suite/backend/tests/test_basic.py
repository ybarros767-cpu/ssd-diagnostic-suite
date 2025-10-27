import asyncio
import sys
from typing import Dict

sys.path.append('/workspace/ssd-diagnostic-suite/backend')

import main  # noqa: E402
from settings import settings  # noqa: E402


async def _auth_token() -> str:
    # Auth desabilitada por padrão: retorna token convidado
    from auth import create_access_token
    return create_access_token('test', 'admin')


def test_imports():
    assert main.app is not None
    assert hasattr(main, 'socket_app')


def test_settings_defaults():
    assert settings.prometheus_port == 9090


def test_health_sync():
    resp: Dict[str, object] = main.health()
    assert resp.get('status') == 'ok'


async def _get_report():
    return await main.get_report(user={})


def test_report_event_loop():
    res = asyncio.get_event_loop().run_until_complete(_get_report())
    assert 'status' in res


def test_login_guest_token():
    # Quando ENABLE_AUTH=false, deve retornar token guest
    from auth import login
    body = {}
    token = login(body)
    assert 'access_token' in token
