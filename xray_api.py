import json
import os
import subprocess
import tempfile

XRAY_BIN = "/usr/local/bin/xray/xray"
XRAY_API = "127.0.0.1:10085"
CONFIG_PATH = "/etc/xray/config.json"
INBOUND_TAG = "vless-in"


def add_vless_user(user_uuid: str, email: str) -> bool:
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)

        for inbound in config.get("inbounds", []):
            if inbound.get("tag") == INBOUND_TAG:
                inbound.setdefault("settings", {})["clients"] = [
                    {
                        "id": user_uuid,
                        "email": email
                    }
                ]
                break
        else:
            return False

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".json",
            delete=False,
            encoding="utf-8"
        ) as f:
            json.dump(config, f, ensure_ascii=False)
            temp_path = f.name

        try:
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

            return (
                result.returncode == 0
                and "Added 1 user" in result.stdout
            )

        finally:
            os.remove(temp_path)

    except Exception:
        return False