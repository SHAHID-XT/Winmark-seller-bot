# Winmark Bot

This is an automated bot for managing products on Winmark Seller using Selenium and ChatGPT for generating SEO-friendly descriptions and keywords. The bot logs in to the Winmark website, navigates through product pages, and updates descriptions and keywords based on predefined settings.

## Requirements

Before running the bot, ensure you have these installed:
- Python 3.6+
- Selenium
- SeleniumBase
- dotenv (`pip install python-dotenv`)

You’ll also need a `.env` file to store your login credentials and settings.

## Environment Variables

Create a `.env` file in the root directory of the project with the following keys:

```plaintext
EMAIL=your_email_here
PASSWORD=your_password_here
SKIP_ALREADY_EXIST=on # Set to "on" to skip updating products with existing descriptions, "off" otherwise.
FILTER_USING_TEXT=Optional_Text_Filter # Text to filter products by name; leave empty if not required.
```

## Key Features

- **Login**: Logs into your Winmark account.
- **Pagination**: Goes through all pages of products.
- **Description & Keywords**: Generates SEO descriptions and keywords using ChatGPT.
- **Product Updates**: Optionally updates products only missing descriptions or those with specific tags.
- **History Tracking**: Keeps track of processed products in a `history.json` file.

## How to Run

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Bot**:
   ```bash
   python main.py
   ```

## Code Overview

- **Winmarkbot Class**: The main class handling the bot operations.
  - `get_driver()`: Initializes the browser driver.
  - `do_login()`: Logs into Winmark Seller.
  - `next_page()`: Navigates to the next page.
  - `get_product_name()`: Gets the current product name.
  - `checkbox_checked()`: Checks the “Prop65” checkbox if needed.
  - `get_product_description()`: Gets or sets the product description.
  - `get_product_keywords()`: Gets or sets product keywords.
  - `Runner()`: Main function that performs the bot tasks page by page.

- **ChatGPT Class**: Helper class to generate SEO content.

## Troubleshooting

If you encounter issues with the bot, try the following:
- Ensure all dependencies are installed.
- Check that your `.env` file is correctly set up.
- Increase timeout values if elements take longer to load on your network.

## Notes

- Make sure to review the `history.json` file periodically to avoid repeated product updates.
- You can set `FILTER_USING_TEXT` to filter specific products by text.
