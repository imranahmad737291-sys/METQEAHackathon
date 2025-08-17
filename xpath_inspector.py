from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import sys

def get_xpath(element):
    components = []
    while element.tag_name.lower() != "html":
        siblings = element.find_elements(By.XPATH, f"./preceding-sibling::{element.tag_name}")
        index = len(siblings) + 1
        components.append(f"{element.tag_name}[{index}]")
        element = element.find_element(By.XPATH, "..")
    components.reverse()
    return "/" + "/".join(components)

def launch_xpath_inspector(url):
    options = Options()
    options.add_experimental_option("detach", True)  # Keeps browser open
    driver = webdriver.Chrome(service=ChromeService(), options=options)
    driver.get(url)

    print("👉 Click on any element in the browser, then return to this window and press Enter.")

    time.sleep(3)
    input("⏳ Waiting for you to click an element... Press Enter when done.")
    try:
        active = driver.switch_to.active_element
        xpath = get_xpath(active)
        print(f"\n✅ Relative XPath: {xpath}")
    except Exception as e:
        print(f"❌ Failed to get XPath: {e}")
    time.sleep(5)
    driver.quit()

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else ""
    if url:
        launch_xpath_inspector(url)
    else:
        print("❌ No URL provided.")
