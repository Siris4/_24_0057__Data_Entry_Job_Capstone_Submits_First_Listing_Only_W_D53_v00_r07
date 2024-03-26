from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup
import requests
import re

# constants:
url = "https://appbrewery.github.io/Zillow-Clone/"

# send request to the website:
response = requests.get(url)
html_doc = response.text

# parse the html:
soup = BeautifulSoup(html_doc, 'html.parser')

# regex patterns for cleaning price strings:
cleanup_pattern = re.compile(r'\+|/mo')

# find all property listings and iterate through each one:
property_listings = []
for article in soup.find_all('article', class_='StyledPropertyCard-c11n-8-84'):
    # extract url:
    link_element = article.find('a', class_='StyledPropertyCardDataArea-anchor', href=True)
    url_link = link_element['href'] if link_element else 'No URL Found'

    # extract price:
    price_element = article.find('span', class_='PropertyCardWrapper__StyledPriceLine')
    price_text = price_element.text if price_element else 'No Price Found'
    cleaned_price = cleanup_pattern.sub('', price_text)

    # extract address:
    address_element = article.find('address', {'data-test': 'property-card-addr'})
    address = address_element.text.strip() if address_element else 'No Address Found'

    # append a dictionary for each listing to the property_listings list:
    property_listings.append({
        'url': url_link,
        'price': cleaned_price,
        'address': address
    })

# initialize selenium webdriver:
chrome_options = Options()
# chrome_options.add_argument("--headless")  # uncomment this line to run in headless mode
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

form_url = "https://forms.gle/72vXFXP9gjXq3Qio8"
driver.get(form_url)


# function to attempt finding an element using different methods:
def find_element(driver, methods):
    for method, selector in methods:
        try:
            return WebDriverWait(driver, 5).until(EC.presence_of_element_located((method, selector)))
        except (NoSuchElementException, ElementNotInteractableException, TimeoutException):
            continue
    raise Exception("Element not found using provided methods.")


# iterate over each property listing and fill out the google form:
for property in property_listings[:1]:  # focusing on the first listing for now
    # Layered Catch Mechanism for each field:
    address_field = find_element(driver, [
        (By.CSS_SELECTOR, "input[aria-labelledby='i1']"),
        (By.XPATH, "//*[@id='mG61Hd']/div[2]/div/div[2]/div[1]/div/div/div[2]/div/div[1]/div/div[1]/input"),
        (By.CSS_SELECTOR,
         "#mG61Hd > div.RH5hzf.RLS9Fe > div > div.o3Dpx > div:nth-child(1) > div > div > div.AgroKb > div > div.aCsJod.oJeWuf > div > div.Xb9hP > input")
    ])

    price_field = find_element(driver, [
        (By.CSS_SELECTOR, "input[aria-labelledby='i5']"),
        (By.XPATH, "//*[@id='mG61Hd']/div[2]/div/div[2]/div[2]/div/div/div[2]/div/div[1]/div/div[1]/input"),
        (By.CSS_SELECTOR,
         "#mG61Hd > div.RH5hzf.RLS9Fe > div > div.o3Dpx > div:nth-child(2) > div > div > div.AgroKb > div > div.aCsJod.oJeWuf > div > div.Xb9hP > input")
    ])

    url_field = find_element(driver, [
        (By.CSS_SELECTOR, "input[aria-labelledby='i9']"),
        (By.XPATH, "//*[@id='mG61Hd']/div[2]/div/div[2]/div[3]/div/div/div[2]/div/div[1]/div/div[1]/input"),
        (By.CSS_SELECTOR,
         "#mG61Hd > div.RH5hzf.RLS9Fe > div > div.o3Dpx > div:nth-child(3) > div > div > div.AgroKb > div > div.aCsJod.oJeWuf > div > div.Xb9hP > input")
    ])

    # Clear and fill the fields:
    address_field.clear()
    address_field.send_keys(property['address'])

    price_field.clear()
    price_field.send_keys(property['price'])

    url_field.clear()
    url_field.send_keys(property['url'])

    # submit the form:
    submit_button = find_element(driver, [
        (By.CSS_SELECTOR, ".NPEfkd.RveJvd.snByac"),
        (By.XPATH, "//*[@id='mG61Hd']/div[2]/div/div[3]/div[1]/div[1]/div/span/span"),
        (By.CSS_SELECTOR,
         "#mG61Hd > div.RH5hzf.RLS9Fe > div > div.ThHDze > div.DE3NNc.CekdCb > div.lRwqcd > div > span > span")
    ])
    submit_button.click()

    # waits for some time after submission if necessary:
    time.sleep(2)

    # If the form is a single submission type, you would need to navigate back to the form URL
    # driver.get(form_url)

input("Press Enter to close the browser...")
driver.quit()

# prints the structured data as a confirmation of what's been processed:
for property in property_listings:
    print(f"URL: {property['url']}, Price: {property['price']}, Address: {property['address']}")
