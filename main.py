import json
import time
from dotenv import load_dotenv
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from seleniumbase import Driver
from dotenv import load_dotenv
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


from gpt import ChatGPT
import time

load_dotenv()


class Winmarkbot:
    skip_already_exist = os.getenv("SKIP_ALREADY_EXIST", "on")
    if skip_already_exist == "on":
        skip_already_exist = True
    else:
        skip_already_exist = False
    driver = None
    EMAIL = os.getenv("EMAIL")
    PASSWORD = os.getenv("PASSWORD")
    text_contains = os.getenv("FILTER_USING_TEXT", None)

    def get_driver(self):
        if self.driver is None:
            driver = Driver(uc=True, undetectable=True, user_data_dir="chrome")
            driver.execute_script("window.open('about:blank', '_blank');")
            self.driver = driver
            return driver
        else:
            return self.driver

    def do_login(self):
        driver = self.get_driver()
        print(">> trying to login...")
        for _ in range(2):
            driver.get("https://winmarkseller.com/products")
            wait = WebDriverWait(driver, 15)
            try:
                wait.until(EC.visibility_of_element_located((By.ID, "email")))
            except:
                if "Logout" in driver.page_source:
                    continue

            driver.find_element(By.ID, "email").send_keys(self.EMAIL)
            driver.find_element(By.ID, "password").send_keys(self.PASSWORD)
            driver.find_element(By.ID, "next").click()
            time.sleep(5)

            if "Logout" in driver.page_source:
                continue

        if "Logout" in driver.page_source:
            print(">> Login Success...")

    def next_page(self):
        driver = self.get_driver()
        time.sleep(2)
        button = driver.find_element(By.XPATH, "//*[@aria-label='pagination']")
        button.find_elements(By.CSS_SELECTOR, "button")[2].click()

    def get_product_name(self):
        driver = self.get_driver()
        for _ in range(40):
            if driver.find_element(By.ID, "ui_product_name").get_attribute("value"):
                break
            time.sleep(0.5)
        return driver.find_element(By.ID, "ui_product_name").get_attribute("value")

    def checkbox_checked(self):
        driver = self.get_driver()
        if (
            driver.find_element(By.ID, "prop65").get_attribute("aria-checked")
            == "false"
        ):
            driver.find_element(By.XPATH, "//*[@for='prop65']").click()

    def get_product_description(self, send_keys):
        driver = self.get_driver()
        if send_keys and self.skip_already_exist:
            text_box = driver.find_element(By.ID, "productDescription").find_element(
                By.CLASS_NAME, "ql-editor"
            )
            if driver.find_element(By.ID, "productDescription").text:
                return
            actions = ActionChains(driver)
            actions.click(text_box)  # Focus on the text box
            actions.send_keys(send_keys)  # Type the message
            actions.perform()
            return
        if send_keys:
            text_box = driver.find_element(By.ID, "productDescription").find_element(
                By.CLASS_NAME, "ql-editor"
            )

            actions = ActionChains(driver)
            actions.click(text_box)  # Focus on the text box
            actions.key_down(Keys.CONTROL).send_keys("a").key_up(
                Keys.CONTROL
            ).send_keys(Keys.BACKSPACE)
            actions.perform()

            actions = ActionChains(driver)
            actions.click(text_box)  # Focus on the text box
            actions.send_keys(send_keys)  # Type the message
            actions.perform()
            return

        return driver.find_element(By.ID, "productDescription").text

    def get_product_keywords(self, send_keys=None):
        driver = self.get_driver()
        if send_keys:
            send_keys = ",".join(
                [
                    f.strip()
                    for f in send_keys.split(",")
                    if not ("top-ranking" in f or "SEO" in f or "keywords" in f)
                ]
            )
        if send_keys and self.skip_already_exist:
            if driver.find_element(By.ID, "search_keywords").text:
                return
            driver.find_element(By.ID, "search_keywords").send_keys(send_keys)
            return

        if send_keys:

            driver.find_element(By.ID, "search_keywords").clear()  # Clear the text box
            driver.find_element(By.ID, "search_keywords").send_keys(send_keys)
        return driver.find_element(By.ID, "search_keywords").text

    def get_element_urls(self):
        text_contains = self.text_contains
        driver = self.get_driver()
        time.sleep(5)
        if text_contains:
            return [
                f.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                for f in driver.find_elements(By.CSS_SELECTOR, "tr")
                if text_contains in f.text
                and "products/edit"
                in f.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
            ]

        return [
            f.get_attribute("href")
            for f in driver.find_elements(
                By.XPATH, "//*[starts-with(@href, 'products/edit')]"
            )
        ]

    def switch_to_first_tab(self):
        driver = self.get_driver()
        driver.switch_to.window(driver.window_handles[0])

    def switch_to_second_tab(self):
        driver = self.get_driver()
        driver.switch_to.window(driver.window_handles[1])

    def Runner(self):
        gpt = ChatGPT()
        driver = self.get_driver()
        self.do_login()
        driver.get("https://winmarkseller.com/products")
        time.sleep(3)
        total_pages = self.get_total_pages()
        counter = 0
        error_counts = 0
        for page in range(1, total_pages + 1):
            print()
            print(f">> {page}/{total_pages} pages")
            self.switch_to_first_tab()
            products_urls = self.get_element_urls()
            print(f">> {len(products_urls)} products found on page: {page}")
            for url in products_urls:
                try:
                    if self.check_and_add_url(url):
                        continue
                    self.switch_to_second_tab()
                    driver.get(url)
                    wait = WebDriverWait(driver, 20)
                    wait.until(
                        EC.visibility_of_element_located((By.ID, "ui_product_name"))
                    )
                    product_name = self.get_product_name()
                    print(f">> Current Product Name: {product_name}")
                    prompt = f"write 1 paragraph description for '{product_name}' using top ranking SEO keywords"
                    description = gpt.send_message(prompt)
                    self.get_product_description(description)
                    self.checkbox_checked()
                    prompt = f"Please give me 15 top ranking SEO keywords, seperated by commas, for {product_name}"
                    keywords = gpt.send_message(prompt)
                    self.get_product_keywords(keywords)
                    self.submit_btn()
                    time.sleep(2)
                except Exception as e:
                    # print(e)
                    print(f">> Error on Product: {url}")
            self.switch_to_first_tab()
            self.next_page()
            time.sleep(2)

    def get_total_pages(self):
        driver = self.get_driver()
        time.sleep(5)
        return int(
            driver.find_element(By.XPATH, "//*[@aria-label='pagination']").text.split(
                " "
            )[-1]
        ) // int(
            driver.find_element(By.XPATH, "//*[@aria-label='pagination']").text.split(
                " "
            )[2]
        )

    def submit_btn(self):
        time.sleep(1)
        driver = self.get_driver()
        try:
            driver.find_element(By.XPATH, "//*[text()='Save Changes']").click()
        except:
            driver.execute_script("window.scrollTo(0, 0);")
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            driver.find_element(By.XPATH, "//*[text()='Save Changes']").click()
        for _ in range(60):
            if "Product updated successfully" in driver.page_source:
                break
            time.sleep(0.5)

    def check_and_add_url(self, url, file_path="history.json"):
        # Check if file exists
        if not os.path.exists(file_path):
            # If file does not exist, create it with an empty list
            with open(file_path, "w") as file:
                json.dump([], file)

        # Read the existing URLs from the file
        with open(file_path, "r") as file:
            data = json.load(file)

        # Check if the URL is already in the file
        if url in data:
            return True
        else:
            # Add the URL to the list and write it back to the file
            data.append(url)
            with open(file_path, "w") as file:
                json.dump(data, file, indent=4)  # Save with indentation for readability
            return False


if __name__ == "__main__":
    print(">> Starting Script...")

d = Winmarkbot()
d.Runner()
