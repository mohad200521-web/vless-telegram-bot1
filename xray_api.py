import os
import json
import tempfile
import subprocess

XRAY_BIN = os.getenv(
    "XRAY_BIN",
    "/usr/local/bin/xray/xray"
)

XRAY_API = os.getenv(
    "XRAY_API",
    "127.0.0.1:10085"
)

XRAY_CONFIG = os.getenv(
    "XRAY_CONFIG",
    "/etc/xray/config.json"
)

INBOUND_TAG = os.getenv("INBOUND_TAG", "vless-in")


def add_vless_user(user_uuid: str, email: str) -> bool:
    temp_path = None

    try:
        with open(XRAY_CONFIG, "r", encoding="utf-8") as f:
            config = json.load(f)

        inbound = next(
            (
                item for item in config.get("inbounds", [])
                if item.get("tag") == INBOUND_TAG
            ),
            None
        )

        if inbound is None:
            print("Xray API error: inbound tag not found")
            return False

        user_config = {
            "inbounds": [{
                **inbound,
                "settings": {
                    **inbound.get("settings", {}),
                    "clients": [{
                        "id": user_uuid,
                        "email": email
                    }]
                }
            }]
        }

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".json",
            encoding="utf-8",
            delete=False
        ) as f:
            json.dump(user_config, f)
            temp_path = f.name

        result = subprocess.run(
            [
                XRAY_BIN,
                "api",
                "adu",
                "--server=" + XRAY_API,
                temp_path
            ],
            capture_output=True,
            text=True,
            timeout=20
        )

        print("Xray API exit code:", result.returncode)
        print("Xray API output:", result.stdout)
        print("Xray API error:", result.stderr)

        return result.returncode == 0

    except Exception as exc:
        print("Xray API exception:", repr(exc))
        return False

    finally:
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)