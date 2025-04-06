from telegram import (  # type: ignore
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)  # Import necessary Telegram classes for updates and inline keyboards
from telegram.ext import (  # type: ignore
    ContextTypes,
)  # Import ContextTypes for type hints in callback functions
import math  # Import math module for calculations (used for pagination)

# MY MODULES
from logger import logger  # Custom logger module for logging information and errors
from jobs_requests import (
    job_sites,  # List of available job sites
    getUpWork,  # Scraper function for UpWork
    imitate_site1,  # Dummy scraper function for testing (site "1")
    format_job_message,  # Function to format job details as HTML text
    split_message,  # Function to split long messages into chunks (max 4096 characters)
)

# Dispatcher mapping site keys to their respective scraper functions.
SCRAPER_DISPATCHER = {
    "upwork": getUpWork,
    "1": imitate_site1,
}


# Generate a navigation keyboard for job positions.
# This keyboard shows "Previous" and "Next" buttons based on the current index
# and the total number of job entries (jobs_length).
def generate_next_job_position_keyboard(index: int = 0, jobs_length: int = 10):
    keyboard = []
    # If current index is greater than 0, add a "Previous" button.
    if index > 0:
        # The callback data is set to (current index - 1) as a string.
        keyboard.append(InlineKeyboardButton("Previous", callback_data=str(index - 1)))
    # If current index is less than the total number of jobs, add a "Next" button.
    if index < jobs_length:
        # The callback data is set to (current index + 1) as a string.
        keyboard.append(InlineKeyboardButton("Next", callback_data=str(index + 1)))
    # Return the keyboard layout as a single row with both buttons.
    return InlineKeyboardMarkup([keyboard])


# Handler for processing a user's text query for job positions.
# It calls the appropriate scraper based on the selected site,
# then displays the first job from the response along with navigation buttons.
async def message_query_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 1
) -> None:
    # If the update is a user message, store the user's query in context.user_data.
    if update.message and update.message.text:
        context.user_data["query"] = update.message.text

    # Retrieve the stored query text.
    query_text = context.user_data.get("query", "")
    if not query_text:
        await update.effective_message.reply_text("No query provided.")
        return

    # Ensure that a job site has been selected.
    if "selected_site" not in context.user_data:
        await update.effective_message.reply_text(
            "Please select a job site from the keyboard first."
        )
        return

    selected_site = context.user_data["selected_site"]
    # Retrieve the scraper function based on the selected job site.
    get_jobs = SCRAPER_DISPATCHER[selected_site]

    # Inform the user that the job search is in progress.
    wait_msg = await update.effective_message.reply_text("Wait a moment, please... :)")

    # Call the scraper function with the stored query text and page number.
    response = await get_jobs(query_text, page)
    if response:
        # Save the fetched job data and current page number for navigation.
        context.user_data["jobs"] = response["data"]
        context.user_data["page"] = response["page"]
        # Initialize the current index for displaying jobs (start at 0).
        current_index = 0

        job_text = "No jobs available"
        try:
            # Format the first job in the response into an HTML-formatted message.
            job_text = format_job_message(response["data"][current_index])
        except KeyError:
            logger.info(f"No job at index {current_index}")
        except Exception as e:
            logger.info("Error getting job from response: %s", e)

        # Generate the navigation keyboard for the current job index.
        keyboard = generate_next_job_position_keyboard(
            index=current_index, jobs_length=len(response["data"])
        )

        # Delete the waiting message before sending the results.
        await wait_msg.delete()

        # Build the final message with a header and the formatted job details.
        final_message = f"<b>Results from {selected_site.capitalize()}:</b>\n{job_text}"
        # Split the final message into chunks if it exceeds Telegram's character limit.
        chunks = split_message(final_message)

        # Send the first chunk along with the navigation keyboard.
        await update.effective_message.reply_html(chunks[0], reply_markup=keyboard)
        # Send any additional chunks as separate messages (without keyboard).
        for chunk in chunks[1:]:
            await context.bot.send_message(
                chat_id=update.effective_message.chat.id, text=chunk, parse_mode="HTML"
            )


# Callback handler for navigating between job positions.
# When a user clicks "Next" or "Previous", the callback data (a number as a string)
# indicates the new job index. The message is then updated accordingly.
async def handle_jobs_positions_keyboard_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    query = update.callback_query
    await query.answer()  # Acknowledge the callback query

    # Delete previously sent extra message chunks (if any).
    extra_chunks = context.user_data.get("extra_chunks_ids", [])
    for msg_id in extra_chunks:
        try:
            await context.bot.delete_message(
                chat_id=query.message.chat.id, message_id=msg_id
            )
        except Exception as e:
            logger.error("Error deleting extra message %s: %s", msg_id, e)
    # Clear the stored extra message IDs.
    context.user_data["extra_chunks_ids"] = []

    try:
        # Parse the new job index from the callback data.
        new_index = int(query.data)
    except ValueError:
        await query.edit_message_text(text="Invalid navigation data!")
        return

    # Retrieve the accumulated jobs array from user_data.
    jobs = context.user_data.get("jobs", [])
    if not jobs:
        await query.edit_message_text(text="No jobs data available!")
        return

    # Check if the new index is within the current jobs array.
    if new_index < 0 or new_index >= len(jobs):
        # If out-of-bounds, delete the current message and fetch the next page.
        try:
            await query.delete_message()
        except Exception as e:
            logger.error("Error deleting main message: %s", e)

        extra_chunks = context.user_data.get("extra_chunks_ids", [])
        for msg_id in extra_chunks:
            try:
                await context.bot.delete_message(
                    chat_id=query.message.chat.id, message_id=msg_id
                )
            except Exception as e:
                logger.error("Error deleting extra message %s: %s", msg_id, e)
        context.user_data["extra_chunks_ids"] = []

        # Increment the page number to fetch new jobs.
        next_page = context.user_data["page"] + 1
        await message_query_handler(update, context, next_page)
        return

    # Format the job message for the new index.
    job_text = format_job_message(jobs[new_index])
    # Generate an updated navigation keyboard using the new index.
    new_keyboard = generate_next_job_position_keyboard(new_index, jobs_length=len(jobs))
    # Build the final message with header and job details.
    final_message = f"<b>Results from {context.user_data.get('selected_site', 'Unknown').capitalize()}:</b>\n{job_text}"
    # Split the message into chunks if necessary.
    chunks = split_message(final_message)

    try:
        # Edit the original message with the first chunk and updated keyboard.
        await query.edit_message_text(
            text=chunks[0], parse_mode="HTML", reply_markup=new_keyboard
        )
        # For any additional chunks, send them as new messages and store their message IDs.
        extra_ids = []
        for chunk in chunks[1:]:
            sent_msg = await context.bot.send_message(
                chat_id=query.message.chat.id, text=chunk, parse_mode="HTML"
            )
            extra_ids.append(sent_msg.message_id)
        context.user_data["extra_chunks_ids"] = extra_ids
    except Exception as e:
        logger.error("Error editing message: %s", e)
        await query.edit_message_text(
            text="An error occurred while updating the message."
        )


# Generate a keyboard for selecting job sites.
# This keyboard is used for initial selection and supports pagination.
def generate_jobs_sites_keyboard(
    job_sites: list[str] = job_sites, page: int = 1, per_page: int = 4
) -> InlineKeyboardMarkup:
    # Calculate the start and end indices for the current page.
    start = (page - 1) * per_page
    end = start + per_page
    # Slice the list of job sites for the current page.
    current_sites = job_sites[start:end]

    # Create buttons for each site in the current slice.
    buttons = [
        InlineKeyboardButton(site, callback_data=f"site: {site}")
        for site in current_sites
    ]

    # Arrange buttons in rows (2 buttons per row in this example).
    keyboard = [buttons[i : i + 2] for i in range(0, len(buttons), 2)]

    # Add navigation buttons for pagination if needed.
    nav_buttons = []
    if page > 1:
        nav_buttons.append(
            InlineKeyboardButton("Previous", callback_data=f"page: {page-1}")
        )
    if end < len(job_sites):
        nav_buttons.append(
            InlineKeyboardButton("Next", callback_data=f"page: {page+1}")
        )
    if nav_buttons:
        keyboard.append(nav_buttons)

    # Add a row showing current page information.
    total_pages = math.ceil(len(job_sites) / per_page)
    keyboard.append(
        [
            InlineKeyboardButton(
                f"Page {page} of {total_pages}", callback_data="page_info"
            )
        ]
    )

    return InlineKeyboardMarkup(keyboard)


# Callback handler for job site selection and pagination.
# This handler processes the callback data for selecting a job site or navigating through the list of sites.
async def handle_jobs_sites_keyboard_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    query = update.callback_query
    await query.answer()  # Acknowledge the callback query

    data = query.data or ""

    if data.startswith("site: "):
        # Extract the site name from the callback data and store it in user_data.
        selected_site = data.split(" ")[1].lower()
        context.user_data["selected_site"] = selected_site
        logger.info(f"User selected job site: {selected_site}")
        # Send a message confirming the selected job site.
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text=f"Job site <b><i>{selected_site}</i></b> selected. Now, type your query for a job search.",
            parse_mode="HTML",
        )
    elif data.startswith("page: "):
        try:
            new_page = int(data.split()[1])
        except ValueError:
            logger.info("Error converting page number to int")
            return

        # Generate a new keyboard for the next page of job sites.
        new_keyboard = generate_jobs_sites_keyboard(job_sites, new_page)
        await query.edit_message_reply_markup(reply_markup=new_keyboard)
    elif data == "page_info":
        # This button is informational; acknowledge it without any further action.
        await query.answer(text="This is the page information.", show_alert=False)
    else:
        await context.bot.send_message(
            chat_id=query.message.chat.id, text="Unrecognized action!"
        )
