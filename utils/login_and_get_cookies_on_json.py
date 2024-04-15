import json
import os
import time
from os import PathLike
from pathlib import Path

from selenium import webdriver
import selenium
from typing import NamedTuple

from selenium.webdriver.remote.webdriver import WebDriver
from tqdm import tqdm


class User(NamedTuple):
    username: str
    password: str


class UserPHPSESSID(NamedTuple):
    user: User
    phpsessid: str

    def for_json(self) -> dict:
        return {
            "username": self.user.username,
            "password": self.user.password,
            "PHPSESSID": self.phpsessid
        }



def login_and_get_cookie(
        _driver: WebDriver,
        _user: User,
        open_close: bool = True
) -> dict[str, dict]:
    import undetected_chromedriver as uc
    from selenium import webdriver
    from selenium.webdriver.support import wait, expected_conditions as EC
    from selenium.webdriver.common.by import By

    driver = _driver

    username = _user.username
    password = _user.password

    if open_close or driver is None:
        chromeOptions = webdriver.ChromeOptions()
        chromeOptions.headless = True
        driver = webdriver.Chrome(options=chromeOptions)

    driver.delete_all_cookies()

    driver.get("https://3ddd.ru/auth/login")

    wait.WebDriverWait(driver, 3).until(EC.visibility_of_element_located((By.TAG_NAME, "form")))

    driver.find_element(By.ID, "inputEmail").send_keys(username)
    driver.find_element(By.ID, "inputPassword").send_keys(password)
    driver.find_element(By.XPATH, "//form//button").submit()

    wait.WebDriverWait(driver, 3).until(
        lambda driver_: driver_.get_cookie("PHPSESSID") is not None
    )

    if open_close:
        driver.close()
        driver.quit()

    return {item.pop("name"): item for item in driver.get_cookies()}


def get_list_of_user_data(path_to_file: Path) -> list[User]:
    return [
        User(_raw_user.get("username"), _raw_user.get("password"))

        for _raw_user in
        json.loads(open(path_to_file).read())
    ]


def get_phpsessid_from_list(_data: list[User], path_to_output: Path, _path_to_chromedriver: str):
    result_with_phpsessid = []
    file = open(path_to_output / ".env.secret", "w+")

    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-ssl-errors=yes')
    options.add_argument('--ignore-certificate-errors')

    driver = webdriver.Remote(_path_to_chromedriver, options=options)

    for user in tqdm(_data, desc="get phpsessid from login data file"):
        _phpsessid: str = login_and_get_cookie(driver, user, open_close=False).get("PHPSESSID").get("value")

        result_with_phpsessid.append(
            UserPHPSESSID(
                user,
                _phpsessid
            ).for_json()
        )

        file.seek(0)
        file.write(
            f"LIST_OF_ACTUAL_PHPSESSID={json.dumps(result_with_phpsessid)}"
        )

    os.environ["LIST_OF_ACTUAL_PHPSESSID"] = f"{json.dumps(result_with_phpsessid)}"

    driver.quit()


def update_phpsessid_list(_data: list[dict], path_to_output: Path, _path_to_chromedriver: str):
    file = open(path_to_output / ".env.secret", "w+")
    list_with_updated_phpsessid = json.loads(file.read())

    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-ssl-errors=yes')
    options.add_argument('--ignore-certificate-errors')

    driver = webdriver.Remote(_path_to_chromedriver, options=options)

    # xuyovi ktor. poxil arajin herdin
    for _raw_user in tqdm(_data, desc="update phpsessid on env and env-file"):
        user = User(_raw_user.get("username"), _raw_user.get("password"))
        _phpsessid: str = login_and_get_cookie(driver, user, open_close=False).get("PHPSESSID").get("value")

        for item in list_with_updated_phpsessid:
            if {
                "username": user.username, "password": user.password
                } == {
                "username": item["username"], "password": item["password"]
            }:
                list_with_updated_phpsessid[
                    list_with_updated_phpsessid.index(item)
                ] = UserPHPSESSID(
                    user,
                    _phpsessid
                ).for_json()
                break

        file.seek(0)
        file.write(
            f"LIST_OF_ACTUAL_PHPSESSID={json.dumps(list_with_updated_phpsessid)}"
        )

    os.environ["LIST_OF_ACTUAL_PHPSESSID"] = f"{json.dumps(list_with_updated_phpsessid)}"

    driver.quit()


if __name__ == '__main__':
    get_phpsessid_from_list([
        User(_raw_user.get("username"), _raw_user.get("password"))

        for _raw_user in
        json.loads(open("/home/suren/Projects/upwork/maroz/parser_and_search/resources/data/data_to_login.json").read())
    ])
