import json
import os
import subprocess
import tempfile

XRAY_BIN = "/usr/local/bin/xray/xray"
XRAY_API = "127.0.0.1:10085"
CONFIG_PATH = "/etc/xray/config.json"
INBOUND_TAG = "vless-in"


def add_vless_user(user_uuid: str, email: str) -> bool:
    temp_path = None

    try:
        # قراءة الإعداد الأساسي
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)

        found = False

        # نبحث عن VLESS inbound
        for inbound in config.get("inbounds", []):
            if inbound.get("tag") == INBOUND_TAG:

                # نرسل للمستخدم الجديد فقط
                inbound.setdefault("settings", {})["clients"] = [
                    {
                        "id": user_uuid,
                        "email": email
                    }
                ]

                found = True
                break

        if not found:
            print("ERROR: VLESS inbound not found")
            return False

        # إنشاء ملف مؤقت لـ Xray API
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".json",
            delete=False,
            encoding="utf-8"
        ) as f:

            json.dump(
                config,
                f,
                ensure_ascii=False,
                indent=2
            )

            temp_path = f.name

        # إضافة المستخدم إلى Xray
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
            timeout=15
        )

        print("XRAY STDOUT:")
        print(result.stdout)

        print("XRAY STDERR:")
        print(result.stderr)

        # نجاح العملية
        if result.returncode != 0:
            return False

        if "Added 1 user" in result.stdout:
            return True

        if "Added 1 user(s) in total" in result.stdout:
            return True

        return False

    except Exception as e:
        print("XRAY ERROR:", e)
        return False

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)