from selenium.webdriver.common.by import By
from seleniumbase import Driver
from selenium.webdriver.common.keys import Keys

import time


class ChatGPT:
    last_reply = None
    driver = None
    last_response = None

    def get_driver(self):
        driver = Driver(uc=True, undetectable=True)
        driver.get("https://chatgpt.com/?q=hello")
        self.set_last_reply(driver)
        return driver

    def set_last_reply(self, driver):
        try:
            self.last_reply = driver.find_elements(
                By.CSS_SELECTOR, '[data-message-author-role="assistant"]'
            )[-1].text
        except:
            pass

    def send_message(self, message):
        if not self.driver or not self.driver.title:
            self.driver = self.get_driver()
        driver = self.driver
        error_count = 0
        while True:
            try:
                driver.find_element(By.XPATH, "//*[text()='Stay logged out']").click()
                time.sleep(1)
            except:
                pass
            try:
                d = driver.find_element(By.ID, "prompt-textarea")
                d.send_keys(message)
                time.sleep(0.5)
                d.send_keys(Keys.ENTER)
                time.sleep(1)
                if (
                    not message
                    == driver.find_elements(
                        By.CSS_SELECTOR, '[data-message-author-role="user"]'
                    )[-1].text
                ):
                    return self.send_message

                return self.read_last_message(driver)
            except Exception as e:
                error_count += 1
                driver.get("https://chatgpt.com/?q=hello")
                time.sleep(5)
            if error_count >= 5:
                print(">> Failed to get message from GPT, after multiple attempts.")
                return None

    def read_last_message(self, driver):
        time.sleep(1)
        content = None
        counter = 0
        while True:
            new = driver.find_elements(
                By.CSS_SELECTOR, '[data-message-author-role="assistant"]'
            )[-1].text
            if content == new:
                counter += 1
            if counter >= 5:
                content = new
                break
            time.sleep(1)
            content = new
            if counter >= 60:
                driver.refresh()
                return self.read_last_message(driver)

        if self.last_response == content:
            driver.refresh()
            return self.read_last_message(driver)
        self.last_response = content
        return content
