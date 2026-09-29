import json
import os
import subprocess
import tempfile


XRAY_BIN = "/usr/local/bin/xray/xray"
XRAY_API = "127.0.0.1:10085"
INBOUND_TAG = "vless-in"


def add_vless_user(user_uuid: str, email: str) -> bool:
    config = {
        "inbounds": [
            {
                "tag": INBOUND_TAG,
                "protocol": "vless",
                "settings": {
                    "clients": [
                        {
                            "id": user_uuid,
                            "email": email
                        }
                    ]
                }
            }
        ]
    }

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".json",
            delete=False
        ) as f:
            json.dump(config, f)
            temp_path = f.name

        result = subprocess.run(
            [
                XRAY_BIN,
                "api",
                "adu",
                f"--server={XRAY_API}",
                temp_path
            ],
            capture_output=True,
            text=True,
            timeout=10
        )

        return result.returncode == 0 and "Added" in result.stdout

    except Exception:
        return False

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)