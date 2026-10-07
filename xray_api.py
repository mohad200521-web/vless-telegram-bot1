import json
import subprocess
import tempfile
import os

XRAY_BIN = os.getenv(
    "XRAY_BIN",
    os.path.expanduser("~/xray/xray")
)

XRAY_API = os.getenv(
    "XRAY_API",
    "127.0.0.1:10085"
)

CONFIG_PATH = os.getenv(
    "CONFIG_PATH",
    os.path.expanduser("~/xray/config/config.json")
)

INBOUND_TAG = os.getenv(
    "INBOUND_TAG",
    "vless-in"
)


def add_vless_user(user_uuid: str, email: str) -> bool:
    temp_path = None

    try:
        print("XRAY BIN:", XRAY_BIN)
        print("XRAY API:", XRAY_API)
        print("XRAY CONFIG:", CONFIG_PATH)

        # قراءة إعداد Xray
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)

        # البحث عن inbound
        target = None

        for inbound in config.get("inbounds", []):
            if inbound.get("tag") == INBOUND_TAG:
                target = inbound
                break

        if target is None:
            print("ERROR: VLESS inbound not found")
            return False

        # قائمة المستخدمين
        clients = (
            target
            .setdefault("settings", {})
            .setdefault("clients", [])
        )

        # منع تكرار UUID
        for client in clients:
            if client.get("id") == user_uuid:
                print("ERROR: UUID already exists")
                return False

        # إضافة المستخدم
        clients.append({
            "id": user_uuid,
            "email": email
        })

        # إرسال inbound فقط
        payload = {
            "inbounds": [target]
        }

        # ملف مؤقت
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".json",
            delete=False,
            encoding="utf-8"
        ) as f:
            json.dump(
                payload,
                f,
                ensure_ascii=False,
                indent=2
            )
            temp_path = f.name

        # إزالة inbound القديم
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
            timeout=20
        )

        print("===== XRAY REMOVE =====")
        print(remove_result.stdout)
        print(remove_result.stderr)

        if remove_result.returncode != 0:
            print("ERROR: Failed to remove old inbound")
            return False

        # إضافة inbound الجديد
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
            timeout=20
        )

        print("===== XRAY ADD =====")
        print(add_result.stdout)
        print(add_result.stderr)

        if add_result.returncode != 0:
            print("ERROR: Failed to add new inbound")
            return False

        print("SUCCESS: VLESS user added")
        return True

    except Exception as e:
        print("XRAY ERROR:", e)
        return False

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)