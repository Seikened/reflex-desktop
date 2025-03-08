"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx
from iconify import icon
from rxconfig import config


class State(rx.State):
    """The app state."""

    ...


def index() -> rx.Component:
    # Welcome Page (Index)
    return rx.container(
        rx.color_mode.button(position="top-right"),
        rx.vstack(
            rx.heading("Welcome to Reflex!", size="9"),
            rx.text(
                "Get started by editing ",
                rx.code(f"{config.app_name}/{config.app_name}.py"),
                size="5",
            ),
            rx.link(
                rx.button("Check out our docs!"),
                href="https://reflex.dev/docs/getting-started/introduction/",
                is_external=True,
            ),
            spacing="5",
            justify="center",
            min_height="85vh",
        ),
        rx.logo(),
        rx.hstack(
        icon("mdi:home", color="blue", width=24),
        icon(icon="fa:arrow-right", height=32, rotate="90deg"),
        icon("simple-icons:python", h_flip=True),
        ),
    )


app = rx.App()
app.add_page(index)
