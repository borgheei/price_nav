import requests
import pandas as pd
import matplotlib.pyplot as plt
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
from matplotlib import font_manager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import arabic_reshaper
from bidi.algorithm import get_display
from concurrent.futures import ThreadPoolExecutor

# Load fund data from JSON
with open("data.json", "r", encoding="utf-8") as f:
    funds = json.load(f)

# URL template for each fund
base_url = "https://tsetmc.com/instInfo/{}"


def fetch_data(idtse):
    url = f"https://tsetmc.com/instInfo/{idtse}"
    CHROMEDRIVER_PATH = "../chromedriver/chromedriver.exe"
    # url = base_url.format(idtse)
    print("idtse: ", url)

    # تنظیمات کروم
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # مسیر کامل به `chromedriver.exe` خودتان را تنظیم کنید
    # service = Service("C:/path/to/chromedriver.exe")



    # Initialize Selenium WebDriver
    # options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # Run in headless mode to avoid opening a window
    service = Service(CHROMEDRIVER_PATH)
    # driver = webdriver.Chrome(service=service, options=options)
    # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(url)

    try:
        driver.get(url)
        time.sleep(3)  # Wait for the page to load

        # استخراج قیمت پایانی از شناسه "d03"
        # price_tag = WebDriverWait(driver, 10).until(
        #     EC.presence_of_element_located((By.ID, "d03")))
        price_tag = driver.find_element(By.ID, "d03")
        price = price_tag.text.split()[0] if price_tag else None

        # استخراج NAV ابطال از شناسه "PRedTran"
        nav_tag = driver.find_element(By.ID, "PRedTran")
        # nav_tag = WebDriverWait(driver, 10).until(
        #     EC.presence_of_element_located((By.ID, "PRedTran")))
        nav = nav_tag.text.split()[0] if nav_tag else None

        print(f"Fund ID: {idtse}")
        print(f"Extracted Price: {price}")
        print(f"Extracted NAV: {nav}")

        # تبدیل به عدد
        price = float(price.replace(",", "")) if price else None
        nav = float(nav.replace(",", "")) if nav else None

        pn_ratio = price / nav if nav else None
        print(f"P/NAV Ratio: {pn_ratio}")
        return pn_ratio

    except Exception as e:
        print(f"Error fetching data for id {idtse}: {e}")
        return None
    finally:
        driver.quit()


# Collect P/NAV data for each fund
def collect_pnav_data():
    pnav_values = {}
    with ThreadPoolExecutor(max_workers=9) as executor:
        results = executor.map(fetch_data, [fund["idtse"] for fund in funds])
        for fund, pnav in zip(funds, results):
            if pnav is not None:
                pnav_values[fund["نماد"]] = pnav
    return pnav_values
    # for fund in funds:
    #     pnav = fetch_data(fund["idtse"])
    #     if pnav is not None:
    #         pnav_values[fund["نماد"]] = pnav
    # return pnav_values


# Plot data
def plot_pnav(pnav_data):
    # font_path = "./Yekan.ttf"
    # font_prop = font_manager.FontProperties(fname=font_path)
    # plt.rcParams['font.family'] = font_prop.get_name()

    names = [get_display(arabic_reshaper.reshape(name)) for name in pnav_data.keys()]
    values = list(pnav_data.values())

    plt.figure(figsize=(10, 5))
    plt.bar(names, values, width=0.2)
    plt.xlabel(get_display(arabic_reshaper.reshape('نام صندوق ها')))
    plt.ylabel(get_display(arabic_reshaper.reshape('P/NAV نسبت')))
    plt.title(get_display(arabic_reshaper.reshape('P/NAV مقایسه نسبتهای')))
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()


# Main loop to update every 3 minutes
while True:
    pnav_data = collect_pnav_data()
    plot_pnav(pnav_data)
    print("start")
    time.sleep(180)  # 3-minute delay
    print("3 min passed")
