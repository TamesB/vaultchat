import os


def _is_production() -> bool:
    env = os.environ
    return (
        env.get("DJANGO_SETTINGS_MODULE") == "config.settings.prod"
        or env.get("APP_ENV", "").lower() == "production"
        or env.get("ENVIRONMENT", "").lower() == "production"
        or bool(env.get("RAILWAY_ENVIRONMENT_NAME"))
    )


module = os.environ.get("DJANGO_SETTINGS_MODULE", "")
if module in {"config.settings.dev", "config.settings.prod"}:
    # Respect an explicit override when the app is started with a specific settings module.
    pass
elif module in {"config.settings", ""}:
    if _is_production():
        from .prod import *  # noqa: F401,F403
    else:
        from .dev import *  # noqa: F401,F403
else:
    # Let a custom settings module decide for itself.
    pass

