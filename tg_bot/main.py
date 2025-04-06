import os
from dotenv import load_dotenv  # Loads environment variables from a .env file
from telegram import (  # type: ignore  # Import Telegram classes
    Update,  # Represents an incoming update (message, callback, etc.)
)
from telegram.ext import (  # type: ignore  # Import extension modules for handling commands, messages, and callbacks
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)

# Import custom modules: commands and keyboard handling functions.
# 'start', 'help_command', 'commands', 'jobs', and 'exit_command' are defined in commands.py
# 'handle_jobs_sites_keyboard_callback', 'message_query_handler', and 'handle_jobs_positions_keyboard_callback'
# are defined in keyboard_handle.py and manage inline keyboard interactions.
from commands import start, help_command, commands, jobs, exit_command
from keyboard_handle import (
    handle_jobs_sites_keyboard_callback,  # Handles callbacks for job site selection and pagination.
    message_query_handler,  # Handles incoming text messages (job queries).
    handle_jobs_positions_keyboard_callback,  # Handles callbacks for navigating job positions.
)

# Load environment variables from the .env file.
load_dotenv()
# Retrieve the bot token from environment variables.
BOT_API = os.getenv("TG_BOT")


def main() -> None:
    """Start the Telegram bot application."""

    # Define an asynchronous post-initialization function to set bot commands.
    async def post_init(application: Application) -> None:
        # Set the bot's commands so that they appear when the user types "/"
        await application.bot.set_my_commands(commands)

    # Create the Application instance and initialize it with the bot's token.
    # The post_init function is called after the application is built.
    application = Application.builder().token(BOT_API).post_init(post_init).build()

    # Register a command handler for the /start command.
    application.add_handler(CommandHandler("start", start))

    # Register a command handler for the /jobs command.
    application.add_handler(CommandHandler("jobs", jobs))

    # Register a callback query handler for job site selection and pagination.
    # This handler will process callback data starting with "site:", "page:", or "page_info".
    application.add_handler(
        CallbackQueryHandler(
            handle_jobs_sites_keyboard_callback, pattern=r"^(site:|page:|page_info)"
        )
    )

    # Register a command handler for the /help command.
    application.add_handler(CommandHandler("help", help_command))

    # Register a command handler for the /exit command.
    application.add_handler(CommandHandler("exit", exit_command))

    # Register a message handler to process text messages that are not commands.
    # This is used for job search queries.
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, message_query_handler)
    )

    # Register a callback query handler for job position navigation.
    # This handler will process callback data that are only digits (e.g., "0", "1", etc.),
    # which represent the job position index.
    application.add_handler(
        CallbackQueryHandler(handle_jobs_positions_keyboard_callback, pattern=r"^\d+$")
    )

    # Start the bot and begin polling for updates.
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()  # Entry point: run the main function if this module is executed directly.
