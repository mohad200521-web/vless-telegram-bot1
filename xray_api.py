import json
import subprocess
import tempfile
import os

XRAY_BIN = "/usr/local/bin/xray/xray"
XRAY_API = "127.0.0.1:10085"
CONFIG_PATH = "/etc/xray/config.json"
INBOUND_TAG = "vless-in"


def add_vless_user(user_uuid: str, email: str) -> bool:
    temp_path = None

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)

        target = None

        for inbound in config.get("inbounds", []):
            if inbound.get("tag") == INBOUND_TAG:
                target = inbound
                break

        if target is None:
            print("ERROR: VLESS inbound not found")
            return False

        clients = target.setdefault("settings", {}).setdefault("clients", [])

        clients.append({
            "id": user_uuid,
            "email": email
        })

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".json",
            delete=False,
            encoding="utf-8"
        ) as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
            temp_path = f.name

        # إزالة الـ inbound القديم
        remove_result = subprocess.run(
            [
                XRAY_BIN,
                "api",
                "rmi",
                "--server",
                XRAY_API,
                INBOUND_TAG
            ],
            capture_output=True,
            text=True,
            timeout=15
        )

        print("XRAY REMOVE:")
        print(remove_result.stdout)
        print(remove_result.stderr)

        # إعادة إضافة الـ inbound بالتكوين الجديد
        add_result = subprocess.run(
            [
                XRAY_BIN,
                "api",
                "adi",
                "--server",
                XRAY_API,
                temp_path
            ],
            capture_output=True,
            text=True,
            timeout=15
        )

        print("XRAY ADD:")
        print(add_result.stdout)
        print(add_result.stderr)

        return add_result.returncode == 0

    except Exception as e:
        print("XRAY ERROR:", e)
        return False

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)