import reflex as rx

class ReflextemplateConfig(rx.Config):
    pass

config = ReflextemplateConfig(
    app_name="reflex_app",
    show_built_with_reflex=False,
    telemetry_enabled=False,
    frontend_port=3000,  # default frontend port
    backend_port=8000,  # default backend port
    # Usa el dominio público en producción
)
