#!/usr/bin/env python3
"""Run failed-login acceptance checks against the isolated Compose stack.

The stack must use ENVIRONMENT=test. No credentials, hashes, cookies, or tokens are
printed. The shortened lockout validates behavior only; production remains 15 minutes.
"""

from __future__ import annotations

import json
import time
from concurrent.futures import ThreadPoolExecutor

from run_session_control_acceptance import psql_scalar, recover_local_otp, request

GENERIC_MESSAGE = "Invalid email or password. Please try again later."


def create_account(label: str, role: str) -> tuple[str, str]:
    suffix = f"{int(time.time() * 1000)}-{label}"
    email = f"login@acceptance-{suffix}.test.sa"
    password = f"Acceptance-{suffix}-Aa9!"
    request(
        "/api/v1/auth/custom-signup",
        body={
            "firstName": "Login",
            "lastName": "Tester",
            "email": email,
            "password": password,
            "companyName": "IIoT Acceptance",
            "industrySector": "Technology",
            "companySize": "1-10",
            "city": "Riyadh",
            "role": role,
        },
    )
    otp = recover_local_otp(email)
    request("/api/v1/auth/verify-signup-otp", body={"email": email, "code": otp})
    stored_role = psql_scalar(f"select role from users where email='{email}'")
    if stored_role != role:
        raise AssertionError(f"Expected disposable {role} role, found {stored_role!r}")
    return email, password


def signin(email: str, password: str, expected: tuple[int, ...]):
    status, headers, payload = request(
        "/api/v1/auth/custom-signin",
        body={"email": email, "password": password},
        expected=expected,
    )
    parsed = json.loads(payload)
    return status, headers, parsed


def assert_failure_sequence(email: str, wrong_password: str) -> list[tuple[int, str]]:
    observed = []
    for attempt in range(1, 6):
        expected = (401,) if attempt < 5 else (429,)
        status, headers, body = signin(email, wrong_password, expected)
        message = body.get("message")
        if message != GENERIC_MESSAGE:
            raise AssertionError(f"Attempt {attempt} returned non-generic feedback")
        if attempt == 5 and int(headers.get("Retry-After", "0")) <= 0:
            raise AssertionError("Fifth failure did not provide a positive Retry-After value")
        observed.append((status, message))
    return observed


def main() -> None:
    started = time.time()
    results = []

    admin_email, admin_password = create_account("admin", "admin")
    admin_sequence = assert_failure_sequence(admin_email, admin_password + "-wrong")
    signin(admin_email, admin_password, (429,))
    results.append("administrator protection activates on fifth consecutive failure: PASS")

    member_email, member_password = create_account("member", "member")
    member_sequence = assert_failure_sequence(member_email, member_password + "-wrong")
    signin(member_email, member_password, (429,))
    results.append("normal-user protection activates on fifth consecutive failure: PASS")

    unknown_email = f"unknown-{int(time.time() * 1000)}@example.test.sa"
    unknown_sequence = assert_failure_sequence(unknown_email, "Not-A-Real-Password-Aa9!")
    if unknown_sequence != member_sequence:
        raise AssertionError("Existing and unknown accounts produced distinguishable failure sequences")
    results.append("unknown and existing accounts receive identical generic failure sequences: PASS")

    concurrent_email, concurrent_password = create_account("concurrent", "member")
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(
                signin,
                concurrent_email,
                concurrent_password + "-wrong",
                (401, 429),
            )
            for _ in range(5)
        ]
        concurrent_results = [future.result() for future in futures]
    concurrent_statuses = sorted(result[0] for result in concurrent_results)
    if concurrent_statuses != [401, 401, 401, 401, 429]:
        raise AssertionError(f"Concurrent threshold was not atomic: {concurrent_statuses}")
    signin(concurrent_email, concurrent_password, (429,))
    results.append("concurrent failures are atomically serialized in shared state: PASS")

    time.sleep(13)
    status, _, body = signin(admin_email, admin_password, (200,))
    if status != 200 or body.get("status") not in ("OK", "MFA_REQUIRED"):
        raise AssertionError("Correct password did not recover after the isolated lockout timer")
    signin(admin_email, admin_password + "-wrong-again", (401,))
    results.append("timer recovery and successful-password counter reset: PASS")

    columns = psql_scalar(
        "select string_agg(column_name, ',' order by ordinal_position) "
        "from information_schema.columns where table_name='login_attempts'"
    )
    if "email" in columns.split(","):
        raise AssertionError("login_attempts unexpectedly stores plaintext email")
    results.append("shared PostgreSQL state stores no plaintext email address: PASS")

    print("\n".join(results))
    print(f"elapsed_seconds={int(time.time() - started)}")
    print("No credentials, hashes, cookies, session handles, or token values were printed.")


if __name__ == "__main__":
    main()
