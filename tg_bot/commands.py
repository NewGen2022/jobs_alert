from telegram import (  # type: ignore
    Update,
    BotCommand,
)  # Import Update and BotCommand from telegram (used to define commands)
from telegram.ext import (  # type: ignore  # Import ContextTypes for type hints in callback functions
    ContextTypes,
)

# MY MODULES
from logger import logger  # Custom logging module for logging info/errors
from keyboard_handle import (
    generate_jobs_sites_keyboard,
)  # Function to generate keyboard for job site selection

# Define the bot commands that will appear in the Telegram client when a user types "/"
commands = [
    BotCommand("start", "Start the bot"),
    BotCommand("help", "Show help information"),
    BotCommand("jobs", "Search for jobs"),
    BotCommand("exit", "Stop interacting with the bot"),
]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler for the /start command.
    Sends a welcome message along with a keyboard for selecting a job site.
    """
    user = update.effective_user  # Get the user object from the update
    logger.info(
        "User %s started the bot", user.username
    )  # Log that the user started the bot

    # Generate the inline keyboard for job site selection
    reply_markup = generate_jobs_sites_keyboard()

    # Send a welcome message with HTML formatting and the generated keyboard attached
    await update.message.reply_html(
        f"Hi {user.mention_html()}! Welcome to <b>Job Beacon</b> – your personal assistant to exciting career opportunities.\n"
        "We bring you real-time alerts from the top job sites, ensuring you never miss a chance to shine.\n"
        "Tap a button below to begin your journey towards your dream job!",
        reply_markup=reply_markup,
    )


async def jobs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler for the /jobs command.
    Sends a message prompting the user to begin their job search.
    """
    await update.message.reply_html(
        "Tap a button below to begin your journey towards your dream job!",
        reply_markup=generate_jobs_sites_keyboard(),  # Attach the job sites keyboard
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler for the /help command.
    Sends a help message.
    """
    await update.message.reply_text("Help! no help command for now :(")


async def exit_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler for the /exit command.
    Clears all stored user data and sends a goodbye message.
    """
    # Clear all stored data for the user in this session.
    context.user_data.clear()

    # Send a goodbye message informing the user that their search history has been cleared.
    await update.message.reply_text(
        "🚪 You've exited the bot. "
        "Your search history has been cleared.\n"
        "Type /start to begin again."
    )
