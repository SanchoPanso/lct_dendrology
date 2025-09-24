import asyncio
import os

from dotenv import load_dotenv

from lct_dendrology import create_application


def main() -> None:
    load_dotenv(".env")
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError(
            "Environment variable TELEGRAM_BOT_TOKEN is not set. "
            "Create a .env file or export the variable."
        )

    application = create_application(token)

    # Use built-in polling runner for simplicity
    application.run_polling(close_loop=False)


if __name__ == "__main__":
    main()



