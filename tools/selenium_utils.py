import json
import logging
import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


def set_driver(headless_mode: bool = False, auto_detach: bool = False,
               download_path: str = None, proxy: str = None) -> webdriver.Chrome:
    """
    Set up the driver
    :param proxy: The Proxy IP, like: http://127.0.0.1:10800
    :param download_path: if not None, change default download path
    :param auto_detach: whether to automatically detach the driver
    :param headless_mode: Whether to use headless mode
    """
    options = Options()
    # 无头模式
    if headless_mode:
        logging.info("Use headless mode")
        options.add_argument('headless')

    # 进程结束自动关闭浏览器
    if not auto_detach:
        options.add_experimental_option("detach", True)

    # 修改下载设置
    if download_path is not None:
        prefs = {'profile.default_content_settings.popups': 0,  # 防止保存弹窗
                 'download.default_directory': download_path,  # 设置默认下载路径
                 "profile.default_content_setting_values.automatic_downloads": 1  # 允许多文件下载
                 }
        options.add_experimental_option('prefs', prefs)

    # 代理
    if proxy is not None:
        options.add_argument(f'--proxy-server={proxy}')

    # 常用设置
    options.add_experimental_option("prefs",
                                    {"credentials_enable_service": False, "profile.password_manager_enabled": False})
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')

    # 隐藏特征
    options.add_argument('ignore-certificate-errors')
    options.add_argument(
        'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/109.0.5414.74 Safari/537.36')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    options.page_load_strategy = "normal"
    driver = webdriver.Chrome(options=options, service=ChromeService(ChromeDriverManager().install()))
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": """
            Object.defineProperty(navigator, 'webdriver', {
              get: () => undefined
            })
          """})

    return driver


def web_wait(driver: webdriver, by: str, element: str, until_sec: int = 20):
    WebDriverWait(driver, until_sec).until(EC.presence_of_element_located((by, element)))


def check_element_exists(driver: webdriver, element: str, find_model=By.CLASS_NAME) -> bool:
    """
    Check whether the element exists
    :param driver: browser drive
    :param element: WebElement
    :param find_model: The selenium locator, default By.CLASS_NAME
    :return: bool, whether the element exists
    """
    try:
        driver.find_element(find_model, element)
        return True
    except Exception:
        return False


def save_cookies(driver: webdriver, save_path: str = "cookies/cookies.json", black_list: list = None):
    """保存cookie到本地文件"""
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    # 筛选cookie
    if black_list is not None:
        cookies = [cookie for cookie in driver.get_cookies() if cookie['name'] not in black_list]
    else:
        cookies = driver.get_cookies()
    with open(save_path, 'w') as f:
        json.dump(cookies, f, sort_keys=True, indent=4)


def load_cookies(driver: webdriver, load_path: str = "cookies/cookies.json"):
    """从本地文件加载cookie"""
    with open(load_path, 'r') as f:
        cookies = json.loads("".join(f.readlines()))
    for cookie in cookies:
        driver.add_cookie({
            'domain': cookie['domain'],
            'name': cookie['name'],
            'value': cookie['value'],
            'path': '/',
            'expires': None
        })
