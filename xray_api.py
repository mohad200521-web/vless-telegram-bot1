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

INBOUND_TAG = os.getenv(
    "INBOUND_TAG",
    "vless-in"
)


def add_vless_user(user_uuid: str, email: str) -> bool:
    try:
        if not os.path.isfile(XRAY_BIN):
            print(f"ERROR: Xray binary not found: {XRAY_BIN}")
            return False

        # تحقق من أن Xray يعمل
        check = subprocess.run(
            [XRAY_BIN, "version"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if check.returncode != 0:
            print("ERROR: Xray version check failed")
            print(check.stderr)
            return False

        # لا نحاول إضافة المستخدم بأمر غير مدعوم.
        # يلزم إعداد API في config.json واستخدام gRPC
        # عبر HandlerService.AddUser.
        print("ERROR: Xray gRPC API configuration is required.")
        print(f"Expected API endpoint: {XRAY_API}")
        print(f"Expected inbound tag: {INBOUND_TAG}")
        print(f"Requested user: {email}")
        return False

    except Exception as exc:
        print("XRAY ERROR:", repr(exc))
        return False