import os
import subprocess

XRAY_BIN = os.getenv(
    "XRAY_BIN",
    "/usr/local/bin/xray/xray"
)

XRAY_API = os.getenv(
    "XRAY_API",
    "127.0.0.1:10085"
)

INBOUND_TAG = os.getenv("INBOUND_TAG", "vless-in")


def add_vless_user(user_uuid: str, email: str) -> bool:
    try:
        result = subprocess.run(
            [
                XRAY_BIN,
                "api",
                "adu",
                "--server=" + XRAY_API,
                "--inbound=" + INBOUND_TAG,
                "--email=" + email,
                "--user=" + user_uuid,
            ],
            capture_output=True,
            text=True,
            timeout=20,
        )

        print("Xray API exit code:", result.returncode)
        print("Xray API output:", result.stdout)
        print("Xray API error:", result.stderr)

        return result.returncode == 0

    except Exception as exc:
        print("Xray API exception:", repr(exc))
        return False