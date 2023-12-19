import logging
import os

# from selenium import webdriver
from seleniumwire import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By

from config import username, password
# from tools.csv2pdf import convert
from tools.logging_utils import log_set
from tools.selenium_utils import set_driver, web_wait, save_cookies, load_cookies

OPENINNOLAB_URL = "https://www.openinnolab.org.cn/"


def login_account(driver: webdriver, user_name: str, pass_word: str):
    """
    执行账号登录操作。

    此函数首先打开登录页面，然后切换到密码登录选项。接着输入用户提供的用户名和密码，并执行登录操作。登录过程中还包括必要地等待和交互，以确保页面元素可交互。

    :param driver: 控制浏览器的 webdriver 对象。
    :param user_name: 字符串，用户的登录用户名。
    :param pass_word: 字符串，用户的登录密码。
    :return: 无返回值。

    此函数假设页面已经完全加载，并且所有的 Web 元素都是可访问的。
    """
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
    """
    切换到“我的群组”页面。

    此函数首先定位并悬停在用户图标上，然后从下拉菜单中选择并点击“我的群组”选项，从而导航到群组页面。

    :param driver: 控制浏览器的 webdriver 对象。
    :param save_cookie: 布尔值，指示是否在切换后保存当前会话的 cookies。默认为 False。
    :return: 无返回值。

    如果启用了 save_cookie，函数将在指定位置保存 cookies。
    """
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
    """
    遍历页面上的群组元素，收集并返回所有群组的名称。

    :param driver: 控制浏览器的 webdriver 对象。
    :return: 包含所有群组名称的列表。
    """
    group_lst = []
    web_wait(driver, By.ID, "contentDetail")
    for index, card in enumerate(
            driver.find_elements(By.CSS_SELECTOR, "#contentDetail div[class*='listWrap'] div[class*='card']")):
        group_lst.append(card.find_element(By.CSS_SELECTOR, "div[class*='schoolName']").text)
    return group_lst


def create_group(driver: webdriver, group_name: str) -> str:
    """
     创建一个新群组。如果指定群组名称已存在，将在名称后加 '_1'。

     :param driver: 控制浏览器的 webdriver 对象。
     :param group_name: 要创建的群组的名称。
     :return: 创建的群组名称。如果原名称已存在，则返回修改后的名称。
     """
    web_wait(driver, By.ID, "contentDetail")

    # 获取现有群组列表
    group_lst = get_group_list(driver)
    if group_name in group_lst:
        logging.warning(f"群组 {group_name} 已存在, 设置为: {group_name}_1")
        group_name = f"{group_name}_1"

    # 创建群组
    web_wait(driver, By.XPATH, "//button/span[text() = '创建群组']", wait_for_clickable=True)
    ActionChains(driver).move_to_element(
        driver.find_element(By.XPATH, "//button/span[text() = '创建群组']")).click().perform()

    web_wait(driver, By.XPATH, "//div[contains(@class, 'dialog')]//header[text() = '创建群组']")
    group_create_dialog = driver.find_element(By.XPATH,
                                              "//div[contains(@class, 'dialog')]//header[text() = '创建群组']/following-sibling::form[contains(@class, 'form')]//input[contains(@class, 'CreateGroup')]")
    ActionChains(driver).move_to_element(group_create_dialog).click().perform()
    group_create_dialog.send_keys(group_name)

    confirm_btn = "//div[contains(@class, 'dialog')]//header[text() = '创建群组']/following-sibling::form[contains(@class, 'form')]//button/span[text() = '确认']"
    web_wait(driver, By.XPATH, confirm_btn, wait_for_clickable=True)
    ActionChains(driver).move_to_element(driver.find_element(By.XPATH, confirm_btn)).click().perform()

    web_wait(driver, By.XPATH,
             f"//*[@id='contentDetail']//div[contains(@class, 'listWrap')]//div[contains(@class, 'card')]//div[text() = '{group_name}']")
    logging.info(f"group {group_name} successful created")
    return group_name


def create_sub_accounts(driver: webdriver, group_name: str, sub_num: int = 45, sub_username: list = None):
    web_wait(driver, By.XPATH,
             f"//*[@id='contentDetail']//div[contains(@class, 'listWrap')]//div[contains(@class, 'card')]//div[text() = '{group_name}']")
    ActionChains(driver).move_to_element(driver.find_element(By.XPATH, f"//div[text() = '{group_name}']/ancestor::div[contains(@class, 'cardContainer')]")).click().perform()

    web_wait(driver, By.XPATH, "//*[@id = 'contentDetail']//div[contains(@class, 'member')]/div[text() = '成员']", wait_for_clickable=True)
    ActionChains(driver).move_to_element(driver.find_element(By.XPATH, "//*[@id = 'contentDetail']//div[contains(@class, 'member')]/div[text() = '成员']")).click().perform()
    web_wait(driver, By.XPATH, "//button[contains(@class, 'openAddUsersBtn')]/span[text() = '批量添加']", wait_for_clickable=True)
    ActionChains(driver).move_to_element(driver.find_element(By.XPATH, "//button[contains(@class, 'openAddUsersBtn')]/span[text() = '批量添加']")).click().perform()

    # 点击添加
    web_wait(driver, By.XPATH, "//span[text() = '新增']/parent::div[contains(@class, 'listFooter')]", wait_for_clickable=True)
    for _ in range(10, sub_num):
        ActionChains(driver).move_to_element(driver.find_element(By.XPATH, "//span[text() = '新增']/parent::div[contains(@class, 'listFooter')]")).click().perform()

    # 如未指定，创建子用户名
    if sub_username is None:
        sub_username = [str(i + 1) for i in range(sub_num)]

    # 设置用户名
    elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'userList')]/div[contains(@class, 'userToAdd')]")
    for index, (sub_name, element) in enumerate(zip(sub_username, elements)):
        input_element = element.find_element(By.XPATH, ".//input[@placeholder = '输入姓名']")
        ActionChains(driver).move_to_element(input_element).click().perform()
        input_element.send_keys(sub_name)
        logging.debug(f"successful create No.{index} sub-account: {sub_name}")

    # 提交
    ActionChains(driver).move_to_element(driver.find_element(By.XPATH, "//button/span[text() = '添加']")).click().perform()
    web_wait(driver, By.XPATH, "//div[text() = '添加成功']/parent::div[contains(@class, 'dialog')]", until_sec=30)

    logging.info(f"successful create {sub_num} accounts")


def main(group_name: str, sub_num: int = 45, use_cookie: bool = False, save_path: str = os.path.dirname(os.path.abspath(__file__))):
    driver = set_driver(
        headless_mode=True,
        auto_detach=False,
        download_path=save_path,
        proxy="http://127.0.0.1:52539",
    )
    driver.get(OPENINNOLAB_URL)
    driver.maximize_window()

    # login
    if use_cookie and os.path.exists("cookies/cookies.json"):
        load_cookies(driver=driver, load_path='cookies/cookies.json')
        driver.refresh()
    else:
        login_account(driver=driver, user_name=username, pass_word=password)
    logging.info("Successful login")

    # switch to group page
    switch_to_group(driver=driver)

    # create group
    group_name = create_group(driver=driver, group_name=group_name)
    create_sub_accounts(driver=driver, group_name=group_name, sub_num=sub_num)

    # export csv to pdf
    # create Sub-accounts
    # convert(os.path.join(save_path, f"{group_name}.csv"), os.path.join(save_path, f"{group_name}.pdf"), delimiter=",")


if __name__ == '__main__':
    log_set(log_level=logging.INFO)
    main(group_name="测试群组001", sub_num=45, use_cookie=False)
