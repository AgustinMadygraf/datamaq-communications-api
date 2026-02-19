import importlib
import os
import sys


def test_main_reexports_fastapi_app() -> None:
    for key, value in {
        "SMTP_HOST": "smtp.example.com",
        "SMTP_FROM": "from@example.com",
        "SMTP_TO_DEFAULT": "to@example.com",
    }.items():
        os.environ[key] = value

    sys.modules.pop("main", None)
    sys.modules.pop("src.infrastructure.fastapi.app", None)

    main_module = importlib.import_module("main")
    fastapi_app_module = importlib.import_module("src.infrastructure.fastapi.app")

    assert main_module.app is fastapi_app_module.app
