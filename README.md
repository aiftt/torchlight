# TLIDB Web Crawler

This script downloads pages from the https://tlidb.com/cn/ website, limited to the "cn/" directory and up to 4 levels of link depth.

## Features

- Crawls only within the specified domain and directory (tlidb.com/cn/)
- Respects a maximum link depth of 4 levels
- **Multithreaded processing for faster downloads**
- Saves HTML content with a structure matching the website's URL paths
- Adds delay between requests to be respectful to the server
- Handles errors gracefully with thread safety

## Requirements

- Python 3.6 or higher
- Required packages: requests, beautifulsoup4

## Installation

1. Clone this repository or download the script files
2. Install the required packages:

```bash
pip install -r requirements.txt
```

## Usage

Run the script with Python:

```bash
python cn_crawler.py
```

The downloaded pages will be saved to the `downloaded_pages` directory by default.

## Customization

You can modify the following variables in the script to customize its behavior:

- `base_url`: The starting URL for crawling
- `save_dir`: The directory where pages will be saved
- `max_depth`: The maximum depth of links to follow (default is 4)
- `num_threads`: The number of concurrent download threads (default is 8)

## Notes

- The script uses multithreading with 8 concurrent threads by default for faster downloads
- Thread synchronization is implemented to ensure thread safety
- Each thread adds a 0.5-second delay between requests to avoid overloading the server
- Pages are saved with their URL structure preserved, creating directories as needed
- Console output shows the crawling progress and any errors encountered 