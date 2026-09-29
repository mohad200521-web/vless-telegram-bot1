import json
import subprocess

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
                    ],
                    "decryption": "none"
                }
            }
        ]
    }

    try:
        result = subprocess.run(
            [
                XRAY_BIN,
                "api",
                "adu",
                f"--server={XRAY_API}",
                "-json",
            ],
            input=json.dumps(config),
            capture_output=True,
            text=True,
            timeout=10
        )

        return result.returncode == 0

    except Exception:
        return False