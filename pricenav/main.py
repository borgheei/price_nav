import matplotlib.pyplot as mpl
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import arabic_reshaper
from bidi.algorithm import get_display
from concurrent.futures import ThreadPoolExecutor


with open("data3.json", "r", encoding="utf-8") as file:
    funds = json.load(file)


def fetch_data(idtse):
    url = f"https://tsetmc.com/instInfo/{idtse}"
    CHROMEDRIVER_PATH = "../chromedriver/chromedriver.exe"

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(url)

    try:
        driver.get(url)
        time.sleep(3)

        price_tag = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "d03")))
        price = price_tag.text.split()[0] if price_tag and price_tag.text.split() else None

        nav_tag = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "PRedTran")))
        nav = nav_tag.text.split()[0] if nav_tag and nav_tag.text.split() else None

        price = float(price.replace(",", "")) if price else None
        nav = float(nav.replace(",", "")) if nav else None
        pn_ratio = price / nav if nav else None
        return pn_ratio

    except Exception as e:
        print(f"Error fetching data for {idtse}: {e}")
        return None
    finally:
        driver.quit()


def collect_pnav_data():
    pnav_values = {}
    with ThreadPoolExecutor(max_workers=6) as executor:
        results = executor.map(fetch_data, [fund["idtse"] for fund in funds])
        for fund, pnav in zip(funds, results):
            if pnav is not None:
                pnav_values[fund["نماد"]] = pnav
    return pnav_values


def mpl_pnav(pnav_data):
    names = [get_display(arabic_reshaper.reshape(name)) for name in pnav_data.keys()]
    values = [round(value, 2) for value in pnav_data.values()]

    mpl.figure(figsize=(10, 5))
    mpl.bar(names, values, width=0.3)
    mpl.xlabel(get_display(arabic_reshaper.reshape('نام صندوق ها')))
    mpl.ylabel(get_display(arabic_reshaper.reshape('P/NAV نسبت')))
    mpl.title(get_display(arabic_reshaper.reshape('P/NAV مقایسه نسبتهای')))
    mpl.xticks(rotation=45, ha="right")

    for i, v in enumerate(values):
        mpl.text(i, v + 0.01, f"{v:.2f}", ha='center', fontsize=6)  # با دقت دو رقم اعشار

    mpl.tight_layout()
    mpl.show()


while True:
    print("start")
    pnav_data = collect_pnav_data()
    mpl_pnav(pnav_data)
    print("end")
    time.sleep(180)
    print("3 min passed")
