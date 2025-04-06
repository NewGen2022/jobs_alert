import httpx
from datetime import datetime
import time

# List of job sites for demonstration purposes.
job_sites = ["UpWork", "1"]
# Mapping of site identifiers to their API endpoints.
jobs_api_url = {"upwork": "http://localhost:9156/api/upwork/jobs"}


# format_job_message formats a job dictionary into an HTML-formatted string for Telegram.
def format_job_message(job: dict) -> str:
    """
    Format a job dictionary into an HTML-formatted string for Telegram messages.

    The job dictionary is expected to have the following keys:
      - 'postingTimestamp': Unix timestamp in milliseconds.
      - 'jobTitle': The title of the job.
      - 'jobHref': A URL linking to the job details.
      - 'description': A description of the job.
      - 'skills': A list of skills required for the job.
    """
    # Extract the posting timestamp; returns None if not present.
    posting_timestamp = job.get("postingTimestamp")
    # Extract the job title, defaulting to "No Title" if absent.
    job_title = job.get("jobTitle", "No Title")
    # Extract the job URL, defaulting to "No Link" if absent.
    job_href = job.get("jobHref", "No Link")
    # Extract the job description, defaulting to "No Description" if absent.
    description = job.get("description", "No Description")
    # Extract the skills list, defaulting to an empty list if absent.
    skills = job.get("skills", [])

    # Convert posting timestamp (in milliseconds) to a human-readable date.
    if posting_timestamp and isinstance(posting_timestamp, (int, float)):
        # Convert milliseconds to seconds and create a datetime object.
        dt = datetime.fromtimestamp(posting_timestamp / 1000)
        # Format the date into a readable string, e.g. "Apr 05, 2025".
        posted_date = dt.strftime("%b %d, %Y")
    else:
        posted_date = "Unknown Date"

    # Join the skills list into a comma-separated string.
    skills_text = ", ".join(skills) if skills else "None"

    # Build the HTML-formatted message with:
    # - Bold text for labels.
    # - Newline characters for formatting.
    # - A clickable link for the job.
    message = (
        f"<b>Job Title:</b> {job_title}\n"
        f"<b>Posted:</b> {posted_date}\n\n"
        f"<b>Description:</b>\n{description}\n\n"
        f"<b>Skills:</b> {skills_text}\n\n"
        f"<b>Job Link:</b> <a href='{job_href}'>Click here</a>"
    )

    return message


def split_message(text: str, max_length: int = 4096) -> list[str]:
    """
    Splits the text into chunks of at most max_length characters.
    Telegram has a maximum message length of 4096 characters,
    so this function helps to divide a long message into smaller parts.
    """
    return [text[i : i + max_length] for i in range(0, len(text), max_length)]


# getUpWork sends an HTTP GET request to the UpWork jobs API endpoint with query parameters.
async def getUpWork(query: str, page: int = 1) -> dict[str]:
    # Create an asynchronous HTTP client with a 15-second timeout.
    async with httpx.AsyncClient(timeout=httpx.Timeout(15.0)) as client:
        # Build the request URL by appending query parameters (q and page).
        response = await client.get(jobs_api_url["upwork"] + f"?q={query}&page={page}")
        # Return a dictionary containing the JSON response data and the page number.
        return {"data": response.json(), "page": page}


# imitate_site1 is a dummy function that simulates a scraper for a job site.
async def imitate_site1(query: str, page: int = 1) -> dict:
    """
    Mock job data for testing site '1'.
    Returns job data in the same structure as getUpWork.
    """

    # Generate mock job data matching the expected format.
    mock_job = {
        "postingTimestamp": int(time.time() * 1000),  # Current time in ms.
        "jobTitle": f"Mock Job for '{query}'",
        "jobHref": "https://example.com/job/1",
        "description": f"This is a test job for query: {query}\nPage: {page}",
        "skills": ["Python", "Testing", "Telegram Bots"],
    }

    # Return the mock job data wrapped in a list to match the real API response.
    return {"data": [mock_job], "page": page}
