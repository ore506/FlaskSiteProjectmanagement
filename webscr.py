from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from bs4 import BeautifulSoup
import csv
import time
import re

class Webscr:
    """
    A web scraping class to extract real estate deal data from nadlan.gov.il.
    It uses Playwright for browser automation and BeautifulSoup for HTML parsing.
    """
    def __init__(self, url):
        """
        Initializes the Webscr with the target URL.

        Args:
            url (str): The initial URL of the page to scrape (e.g., the first page of deals).
        """
        self.url = url

    def webExe(self, max_pages_to_scrape=10):
        """
        Executes the web scraping process, iterating through multiple pages by clicking
        a "next page" button. Launches a browser, navigates to each page, extracts
        table data, and appends it to a CSV file. Includes a retry mechanism for page loading.
        It also collects all scraped data into a list and returns it.

        Args:
            max_pages_to_scrape (int): The maximum number of pages to attempt to scrape.
                                       The scraping will stop earlier if the "next page"
                                       button is no longer found or if a page fails to load.

        Returns:
            list: A list of lists, where each inner list represents a row of scraped data.
        """
        # Initialize a list to hold all scraped data
        all_scraped_data = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()

            csv_file_path = 'nadlan_deals.csv'
            # Initialize CSV file with headers.
            # 'w' mode will overwrite the file if it exists, ensuring a clean start.
            with open(csv_file_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                headers = ['Deal ID', 'Address', 'Date', 'Price', 'Details', 'Type', 'Rooms', 'Floor', 'Change']
                writer.writerow(headers)
                # Add headers to the all_scraped_data list as the first row
                all_scraped_data.append(headers)
            print(f"CSV file '{csv_file_path}' initialized with headers.")

            current_page_num = 1
            while current_page_num <= max_pages_to_scrape:
                print(f"\n--- Attempting to scrape page {current_page_num} ---")

                max_retries = 3
                page_had_new_data = False
                current_page_data_count = 0

                for attempt in range(max_retries):
                    try:
                        if current_page_num == 1:
                            print(f"Navigating to initial URL: {self.url}")
                            page.goto(self.url, wait_until="domcontentloaded", timeout=60000)
                            page.screenshot(path="nadlan_page_1_initial.png")
                            print("Screenshot saved to nadlan_page_1_initial.png for debugging.")

                        print(f"Page {current_page_num} content check (attempt {attempt + 1}).")

                        try:
                            page.wait_for_selector("table", timeout=10000)
                            print(f"Table element found on page {current_page_num}.")
                        except PlaywrightTimeoutError:
                            print(f"No table found on page {current_page_num} within 10 seconds. This page might be empty or malformed.")
                            page_had_new_data = False
                            break

                        content = page.content()
                        soup = BeautifulSoup(content, 'html.parser')

                        table = soup.find('table')
                        if table:
                            rows = table.find_all('tr')
                            if len(rows) > 1:
                                current_page_data_count = len(rows) - 1
                                with open(csv_file_path, 'a', newline='', encoding='utf-8') as file:
                                    writer = csv.writer(file)
                                    for row in rows[1:]: # Skip header row
                                        cols = row.find_all('td')
                                        cols_data = [col.text.strip() for col in cols[:9]]
                                        writer.writerow(cols_data)
                                        # Add the scraped row to our list
                                        all_scraped_data.append(cols_data)
                                print(f"Data from page {current_page_num} successfully appended to {csv_file_path} and collected.")
                                page_had_new_data = True
                            else:
                                print(f"Page {current_page_num}: Table found, but it contains no new data rows (only header or empty).")
                                page_had_new_data = False
                        else:
                            print(f"Page {current_page_num}: No table element found. This page likely contains no data.")
                            page_had_new_data = False

                        break

                    except PlaywrightTimeoutError as e:
                        print(f"Attempt {attempt + 1} for page {current_page_num} failed due to Playwright timeout: {e}")
                        if attempt < max_retries - 1:
                            print("Retrying page navigation for current page...")
                            time.sleep(2)
                        else:
                            print(f"Max retries reached for page {current_page_num}. Skipping this page.")
                            with open(f'nadlan_error_page_{current_page_num}.html', 'w', encoding='utf-8') as file:
                                page_content_on_error = page.content() if page else "Page content not available."
                                file.write(page_content_on_error)
                            page_had_new_data = False
                            break

                    except Exception as e:
                        print(f"An unexpected error occurred on page {current_page_num} (attempt {attempt + 1}): {e}")
                        with open(f'nadlan_error_page_{current_page_num}.html', 'w', encoding='utf-8') as file:
                            page_content_on_error = page.content() if page else "Page content not available."
                            file.write(page_content_on_error)
                        page_had_new_data = False
                        break

                if not page_had_new_data and current_page_num > 1:
                    print(f"No new data found on page {current_page_num}. Ending the scraping process.")
                    break

                current_page_num += 1

                next_button_selector = 'a:has-text("הבא")'

                try:
                    next_button = page.locator(next_button_selector)
                    if next_button.is_visible():
                        print(f"Clicking next page button for page {current_page_num}...")
                        next_button.click()
                        page.wait_for_load_state('networkidle', timeout=30000)
                        page.wait_for_selector("table", timeout=10000)
                        print(f"Successfully clicked next and loaded page {current_page_num}.")
                    else:
                        print(f"Next page button '{next_button_selector}' not found or not visible. Assuming end of pagination.")
                        break
                except PlaywrightTimeoutError:
                    print(f"Timeout waiting for next page content after clicking. Assuming end of pagination or an issue.")
                    break
                except Exception as e:
                    print(f"An error occurred while trying to click next page: {e}. Assuming end of pagination.")
                    break

            context.close()
            browser.close()
            print("Browser closed.")
        
        # Return all the collected data
        return all_scraped_data

# Main execution block
# if __name__ == "__main__":
#     i_gush = "6631"
#     i_chelka = "215"
#     url = "https://www.nadlan.gov.il/?view=kparcel_all&id=" + i_gush + "-" + i_chelka + "&page=deals"

#     webinc = Webscr(url)
    
#     # Call webExe and store the returned data
#     scraped_results = webinc.webExe(max_pages_to_scrape=10)
    
#     # You can now work with the 'scraped_results' list, e.g., print it or process it further
#     if scraped_results:
#         print("\n--- Scraped Data (first 5 rows): ---")
#         for row in scraped_results[:5]: # Print first 5 rows for review
#             print(row)
#         print(f"\nTotal rows scraped and returned: {len(scraped_results)}")
#     else:
#         print("\nNo data was scraped or returned.")