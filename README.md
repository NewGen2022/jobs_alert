# Job Beacon: Multi-Platform Job Search & Telegram Bot

Job Beacon is a multi-platform application that aggregates job listings from various sources and provides an intuitive interface via Telegram. The system consists of two main components:

- **Node.js API**: Scrapes job platforms (primarily UpWork) and serves data via REST API
- **Python Telegram Bot**: Interactive interface for job searching and navigation

## ✨ Key Features

### 🔍 Job Aggregation Engine
- **Multi-Source Scraping**
  - UpWork integration via Puppeteer
  - Expandable architecture for new platforms
- **Smart Pagination**
  - Automatic page fetching during navigation
  - Results aggregation across multiple pages

### 🤖 Telegram Bot Interface
  - Inline keyboards for job site selection
  - Previous/Next buttons for job browsing
  - User session preservation
  - Query history tracking
  - /exit command with hard lock
  - Clean session termination

## 🛠 Tech Stack

### Backend Services
| Component        | Technology Stack               |
|------------------|---------------------------------|
| Web Scraping     | Node.js, Puppeteer |
| Job API          | REST API, HTTP/JSON, Express.js |
| Telegram Bot     | Python, python-telegram-bot    |
| Async Operations | HTTPX, Asyncio                 |

## 🏃‍♀ Running the System

### Start API Server and Launch Telegram Bot

```
cd api
node server.js

cd tg_bot
python main.py
```

### 🤖 Bot Commands
| Command   |	Description	Example |
------------|-----------------------------------
| /start	  | Initialize bot session | 
| /jobs	    | Start new job search   |
| /help	    | Show help documentation|
| /exit	    | Terminate current session	|
