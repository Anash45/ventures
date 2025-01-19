from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import json
import time

# Path to the ChromeDriver
current_dir = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the script
driver_path = os.path.join(current_dir, "chromedriver-win64", "chromedriver.exe")

# Configure the WebDriver with Service
service = Service(driver_path)
driver = webdriver.Chrome(service=service)

# Open the target URL
url = "https://foundersfund.com/portfolio/"  # Replace with the actual URL
driver.get(url)

# Initialize WebDriverWait
wait = WebDriverWait(driver, 10)

# Wait for the main container to load
container = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "blog-main")))

# Find all the portfolio tiles (links and logos)
tiles = container.find_elements(By.CSS_SELECTOR, ".portfolio-tile")

# Initialize an empty list to store the data
data = []

# Scroll after processing 3 links
scroll_after = 4
card_height = 200  # Adjust this based on your inspection of the card height

# Loop through each tile to extract the necessary information
for index, tile in enumerate(tiles):
    try:
        # Extract the link (href)
        link_element = tile.find_element(By.CSS_SELECTOR, "a")
        href = link_element.get_attribute("href")

        # Extract the background image URL (logo)
        bg_image_element = tile.find_element(By.CSS_SELECTOR, ".tile-bg")
        style = bg_image_element.get_attribute("style")
        logo_url = style.split("background-image: url(")[1].split(")")[0].replace('"', '')

        # Print the href to debug
        print(f"Attempting to click on: {href}")

        # Click on the link to open the overlay popup
        link_element.click()

        # Wait for the overlay to appear
        overlay = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "overflow-scroll.overlay.fixed")))

        # Extract company data from the overlay
        company_data = {}

        # Extract company category
        category = overlay.find_element(By.CSS_SELECTOR, "h4.h5.mb1.green.caps").text
        company_data['category'] = category

        # Extract company name
        company_name = overlay.find_element(By.CSS_SELECTOR, "h1.h2.mb1.font-primary").text
        company_data['name'] = company_name

        # Extract company description
        description = overlay.find_element(By.CSS_SELECTOR, "div.mt2.mb2.pr4 p").text
        company_data['description'] = description

        # Extract founders
        founders_section = overlay.find_elements(By.CSS_SELECTOR, "h4.h5.mb1.green + p a")
        founders = []
        for founder in founders_section:
            founders.append({
                "name": founder.text,
                "linkedin": founder.get_attribute("href")
            })
        company_data['founders'] = founders

        # Extract profiles (websites, Twitter, etc.)
        profiles_section = overlay.find_elements(By.CSS_SELECTOR, "h4.h5.mb1.green + div p a")
        profiles = []
        for profile in profiles_section:
            profiles.append({
                "name": profile.text,
                "url": profile.get_attribute("href")
            })
        company_data['profiles'] = profiles

        # Append company data to the list
        data.append({
            "link": href,
            "logo": logo_url,
            "company_data": company_data
        })

        # Wait for 1 second after clicking the link
        time.sleep(1)

        # Close the overlay by clicking the close button
        close_button = overlay.find_element(By.CSS_SELECTOR, ".btn-close")
        close_button.click()

        # Wait for 1 second after closing the overlay before continuing to the next card
        time.sleep(1)

        # Scroll down after processing every 3 links
        if (index + 1) % scroll_after == 0:
            print("Scrolling the page to load more cards...")
            driver.execute_script(f"window.scrollBy(0, 475);")
            time.sleep(1)  # Wait a bit after scrolling

    except Exception as e:
        # Log the error and continue to the next element
        print(f"Error processing {href if 'href' in locals() else 'unknown'}: {str(e)}")

# Save data to a JSON file
with open("data.json", "w") as file:
    json.dump(data, file, indent=4)

# Print the results (optional)
print("Data has been saved to 'data.json'")
for item in data:
    print(item)

# Close the browser
driver.quit()
