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
        # قراءة إعداد Xray
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)

        # البحث عن VLESS inbound
        target = None

        for inbound in config.get("inbounds", []):
            if inbound.get("tag") == INBOUND_TAG:
                target = inbound
                break

        if target is None:
            print("ERROR: VLESS inbound not found")
            return False

        # الحصول على قائمة المستخدمين
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

        # إضافة المستخدم الجديد
        clients.append({
            "id": user_uuid,
            "email": email
        })

        # مهم:
        # إرسال الـ inbound فقط وليس config.json بالكامل
        payload = {
            "inbounds": [target]
        }

        # إنشاء ملف مؤقت
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

        # حذف الـ inbound القديم من Xray
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

        print("XRAY REMOVE:")
        print(remove_result.stdout)
        print(remove_result.stderr)

        if remove_result.returncode != 0:
            print("ERROR: Failed to remove old inbound")
            return False

        # إضافة الـ inbound الجديد
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

        print("XRAY ADD:")
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