import os
import subprocess

XRAY_BIN = os.getenv(
    "XRAY_BIN",
    os.path.expanduser("~/xray/xray")
)

XRAY_API = os.getenv(
    "XRAY_API",
    "127.0.0.1:10085"
)

INBOUND_TAG = os.getenv(
    "INBOUND_TAG",
    "vless-in"
)


def add_vless_user(user_uuid: str, email: str) -> bool:
    try:
        print("===== XRAY SETTINGS =====")
        print("XRAY BIN:", XRAY_BIN)
        print("XRAY API:", XRAY_API)
        print("INBOUND TAG:", INBOUND_TAG)

        # التأكد من وجود Xray
        if not os.path.isfile(XRAY_BIN):
            print("ERROR: Xray binary not found")
            return False

        # عرض طريقة أمر إضافة المستخدم في نسخة Xray الموجودة
        help_result = subprocess.run(
            [
                XRAY_BIN,
                "help",
                "api",
                "adi"
            ],
            capture_output=True,
            text=True,
            timeout=10
        )

        print("===== XRAY API ADI HELP =====")
        print(help_result.stdout)
        print(help_result.stderr)

        # إضافة المستخدم عبر Xray API
        result = subprocess.run(
            [
                XRAY_BIN,
                "api",
                "adi",
                "--server",
                XRAY_API,
                "--inbound-tag",
                INBOUND_TAG,
                "--id",
                user_uuid,
                "--email",
                email
            ],
            capture_output=True,
            text=True,
            timeout=20
        )

        print("===== XRAY API RESULT =====")
        print("RETURN CODE:", result.returncode)
        print("STDOUT:")
        print(result.stdout)
        print("STDERR:")
        print(result.stderr)

        if result.returncode != 0:
            print("ERROR: Failed to add VLESS user")
            return False

        print("SUCCESS: VLESS user added")
        return True

    except Exception as e:
        print("XRAY ERROR:", repr(e))
        return False