#!/usr/bin/env python3
"""Run accelerated session-control acceptance tests against the isolated Compose stack.

The stack must use ENVIRONMENT=test. This script creates disposable accounts, recovers
the locally generated OTP from its one-way hash by enumerating the six-digit test
space, and never prints credentials, cookies, or tokens.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPOSE = ROOT / "docker/session-control-acceptance-compose.yml"
BASE = "http://127.0.0.1:18000"


@dataclass
class SessionTokens:
    access: str
    refresh: str


def request(path: str, *, body=None, headers=None, expected=(200, 204)):
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(
        BASE + path,
        data=data,
        headers={"Content-Type": "application/json", **(headers or {})},
        method="POST" if body is not None else "GET",
    )
    try:
        response = urllib.request.urlopen(req, timeout=30)
    except urllib.error.HTTPError as exc:
        response = exc
    payload = response.read()
    if response.status not in expected:
        raise AssertionError(f"{path}: expected {expected}, got {response.status}: {payload[:200]!r}")
    return response.status, response.headers, payload


def psql_scalar(sql: str) -> str:
    result = subprocess.run(
        [
            "docker", "compose", "-p", "p2p-session-acceptance", "-f", str(COMPOSE),
            "exec", "-T", "postgres", "psql", "-U", "p2p_test", "-d", "p2p_acceptance",
            "-Atc", sql,
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def recover_local_otp(email: str) -> str:
    digest = psql_scalar(
        "select code_hash from otp_codes "
        f"where email='{email}' and purpose='signup_verify' and used=false "
        "order by created_at desc limit 1"
    )
    if not digest:
        raise AssertionError("No isolated signup OTP was stored")
    for number in range(1_000_000):
        code = f"{number:06d}"
        if hashlib.sha256(code.encode()).hexdigest() == digest:
            return code
    raise AssertionError("Could not recover isolated six-digit OTP")


def new_session(label: str, role: str = "admin") -> SessionTokens:
    suffix = f"{int(time.time() * 1000)}-{label}"
    email = f"session@acceptance-{suffix}.test.sa"
    password = f"Acceptance-{suffix}-Aa9!"
    signup = {
        "firstName": "Session", "lastName": "Tester", "email": email,
        "password": password, "companyName": "IIoT Acceptance",
        "industrySector": "Technology", "companySize": "1-10", "city": "Riyadh",
        "role": role,
    }
    request("/api/v1/auth/custom-signup", body=signup)
    otp = recover_local_otp(email)
    _, headers, _ = request(
        "/api/v1/auth/verify-signup-otp",
        body={"email": email, "code": otp},
    )
    access = headers.get("st-access-token")
    refresh = headers.get("st-refresh-token")
    if not access or not refresh:
        raise AssertionError("SuperTokens did not issue header-mode session tokens")
    stored_role = psql_scalar(f"select role from users where email='{email}'")
    if stored_role != role:
        raise AssertionError(f"Expected disposable {role} role, found {stored_role!r}")
    return SessionTokens(access, refresh)


def authenticated(tokens: SessionTokens, *, expected=(204,)):
    return request(
        "/api/v1/auth/session-activity",
        body={},
        headers={"Authorization": f"Bearer {tokens.access}", "rid": "session"},
        expected=expected,
    )


def main() -> None:
    started = time.time()
    results = []

    idle = new_session("idle-admin", role="admin")
    authenticated(idle)
    time.sleep(46)
    authenticated(idle, expected=(401,))
    results.append("administrator idle expiry at accelerated 45-second boundary: PASS")

    absolute = new_session("absolute-member", role="member")
    for _ in range(6):
        authenticated(absolute)
        time.sleep(25)
    authenticated(absolute, expected=(401,))
    results.append("normal-user absolute expiry at accelerated 150-second boundary despite activity: PASS")

    rotating = new_session("refresh")
    _, refresh_headers, _ = request(
        "/api/v1/auth/session/refresh",
        body={},
        headers={"Authorization": f"Bearer {rotating.refresh}", "rid": "session"},
    )
    rotated_access = refresh_headers.get("st-access-token")
    rotated_refresh = refresh_headers.get("st-refresh-token")
    if not rotated_access or not rotated_refresh or rotated_refresh == rotating.refresh:
        raise AssertionError("Refresh-token rotation was not observed")
    rotating = SessionTokens(rotated_access, rotated_refresh)
    authenticated(rotating)
    results.append("refresh rotation while policy valid: PASS")

    request(
        "/api/v1/auth/signout",
        body={},
        headers={"Authorization": f"Bearer {rotating.access}", "rid": "session"},
    )
    authenticated(rotating, expected=(401,))
    results.append("manual logout revocation: PASS")

    print("\n".join(results))
    print(f"elapsed_seconds={int(time.time() - started)}")
    print("No credentials, cookies, session handles, or token values were printed.")


if __name__ == "__main__":
    main()
