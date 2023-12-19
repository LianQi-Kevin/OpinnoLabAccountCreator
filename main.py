import logging
import os

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By

from config import username, password
from tools.logging_utils import log_set
from tools.selenium_utils import set_driver, web_wait, save_cookies, load_cookies

OPENINNOLAB_URL = "https://www.openinnolab.org.cn/"


def login_account(driver: webdriver, user_name: str, pass_word: str):
    """登录账号"""
    # 打开登录页
    web_wait(driver, By.XPATH, "//button/span[text() = '登录']")
    ActionChains(driver).move_to_element(
        driver.find_element(By.XPATH, "//button/span[text() = '登录']")).click().perform()

    # 切换到密码登录
    pwd_login_btn_Xpath = "//div[contains(@class, 'login-title')]//div[text() = '密码登录']"
    web_wait(driver, By.XPATH, pwd_login_btn_Xpath)
    ActionChains(driver).move_to_element(driver.find_element(By.XPATH, pwd_login_btn_Xpath)).click().perform()

    # 输入账号密码
    web_wait(driver, By.ID, "normal_login_account")
    ActionChains(driver).move_to_element(driver.find_element(By.ID, "normal_login_account")).click().perform()
    driver.find_element(By.ID, "normal_login_account").send_keys(user_name)
    ActionChains(driver).move_to_element(driver.find_element(By.ID, "normal_login_password")).click().perform()
    driver.find_element(By.ID, "normal_login_password").send_keys(pass_word)

    # 点击登陆
    ActionChains(driver).move_to_element(driver.find_element(By.XPATH, "//button[text() = '登录']")).click().perform()

    # 过检测
    web_wait(driver, By.ID, "hv")
    ActionChains(driver).move_to_element(driver.find_element(By.ID, "hv")).perform()
    web_wait(driver, By.ID, "sm-btn-bg")
    ActionChains(driver).move_to_element(driver.find_element(By.ID, "sm-btn-bg")).click().perform()


def switch_to_group(driver: webdriver, save_cookie: bool = False):
    """点击我的群组切换到群组页"""
    web_wait(driver, By.XPATH, "//div[contains(@class, 'userButton')]")
    user_icon = driver.find_element(By.XPATH, "//div[contains(@class, 'userButton')]")
    ActionChains(driver).move_to_element(user_icon).perform()
    web_wait(driver, By.XPATH, "//div[contains(@class, 'menuDropdown')]//li[text() = '我的群组']")
    drop_menu = driver.find_element(By.XPATH, "//div[contains(@class, 'menuDropdown')]//li[text() = '我的群组']")
    ActionChains(driver).move_to_element(drop_menu).click().perform()
    web_wait(driver, By.ID, "contentDetail")

    if save_cookie:
        save_cookies(driver, 'cookies/cookies.json', None)


def get_group_list(driver: webdriver):
    """获取群组列表"""
    group_lst = []
    web_wait(driver, By.ID, "contentDetail")
    for index, card in enumerate(
            driver.find_elements(By.CSS_SELECTOR, "#contentDetail div[class*='listWrap'] div[class*='card']")):
        group_lst.append(card.find_element(By.CSS_SELECTOR, "div[class*='schoolName']").text)
    return group_lst


def create_group(driver: webdriver, group_name: str, group_desc: str = None):
    """创建群组"""
    web_wait(driver, By.ID, "contentDetail")

    # 获取现有群组列表
    group_lst = get_group_list(driver)
    print(group_lst)

    # web_wait(driver, By.XPATH, "//div[contains(@class, 'menuDropdown')]//li[text() = '创建群组']")
    # drop_menu = driver.find_element(By.XPATH, "//div[contains(@class, 'menuDropdown')]//li[text() = '创建群组']")


def main(sub_num: int = 45, use_cookie: bool = False):
    driver = set_driver(
        headless_mode=False,
        auto_detach=False,
        download_path="./",
        proxy="http://127.0.0.1:52539",
    )
    driver.get(OPENINNOLAB_URL)
    driver.maximize_window()

    # login
    if use_cookie and os.path.exists("cookies/cookies.json"):
        load_cookies(driver, 'cookies/cookies.json')
        driver.refresh()
    else:
        login_account(driver, username, password)
    logging.info("Successful login")

    # switch to group page
    switch_to_group(driver)

    # create group
    create_group(driver, "test")


if __name__ == '__main__':
    log_set(log_level=logging.INFO)
    main(sub_num=10, use_cookie=False)
