import json
import os
import time
from os import PathLike
from pathlib import Path
from time import sleep

import requests
# import webdriver_manager.chrome
from selenium import webdriver
# from seleniumwire import webdriver
# import selenium
from typing import NamedTuple

from selenium.webdriver.remote.remote_connection import RemoteConnection
from selenium.webdriver.remote.webdriver import WebDriver
from tqdm import tqdm

from api.api import API
from docker_automation.selenium_standalone import SeleniumStandaloneContainerRunner


class User(NamedTuple):
    username: str
    password: str


class UserPHPSESSID(NamedTuple):
    user: User
    phpsessid: str
    jwt: dict

    def for_json(self) -> dict:
        return {
            "username": self.user.username,
            "password": self.user.password,
            "PHPSESSID": self.phpsessid,
            "BEARER_TOKEN": self.jwt.get("skyAuthToken"),
            "REFRESH_TOKEN": self.jwt.get("skyRefreshToken")
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

    wait.WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.TAG_NAME, "form")))

    driver.find_element(By.ID, "inputEmail").send_keys(username)
    driver.find_element(By.ID, "inputPassword").send_keys(password)
    driver.find_element(By.XPATH, "//form//button").submit()

    wait.WebDriverWait(driver, 60).until(
        lambda driver_: driver_.get_cookie("PHPSESSID") is not None
    )

    if open_close:
        driver.close()
        driver.quit()

    return {item.pop("name"): item for item in driver.get_cookies()}


def get_bearer_token_from_log(_driver: WebDriver) -> str:
    _driver.get("https://3ddd.ru")
    _driver.get_log("performance")
    _driver.refresh()

    data = _driver.get_log("performance")

    filtered_data = list(
        filter(lambda log_item: "Bearer" in log_item["message"] and "/api/view" in log_item["message"], data)
    )

    serialized_data = [json.loads(item["message"]) for item in filtered_data]

    # filtered_req_list = list(filter(lambda req: req.method == "POST" and "/api/view" in req.url and req.headers.get("Authorization"), _driver.requests))
    if len(serialized_data) >= 1:
        return serialized_data[0]["message"]["params"]["request"]["headers"]["Authorization"]


def get_bearer_token(_driver: WebDriver) -> dict:
    local_storage = _driver.execute_script("return localStorage")
    return {
        "skyAuthToken": local_storage.get("skyAuthToken"),
        "skyRefreshToken": local_storage.get("skyRefreshToken")
    }


def get_list_of_user_data(path_to_file: Path) -> list[User]:
    return [
        User(_raw_user.get("username"), _raw_user.get("password"))

        for _raw_user in
        json.loads(open(path_to_file).read())
    ]


def _get_login_datas_from_list(_data: list[User], path_to_output: Path, _path_to_chromedriver: str):
    result_with_phpsessid = []
    file = open(path_to_output / ".env.secret", "w+")

    options = webdriver.ChromeOptions()
    # options.add_argument('--ignore-ssl-errors=yes')
    # options.add_argument('--ignore-certificate-errors')
    # options.add_argument('--disable-blink-features=AutomationControlled')

    # options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

    # options_ = {
    #     'addr': "172.17.0.2",
    # }
    # RemoteConnection.set_timeout(60)
    # driver = RemoteConnection(_path_to_chromedriver)


    driver = webdriver.Remote(_path_to_chromedriver, options=options)
    # driver.timeouts
    # driver = webdriver.Chrome(service=webdriver.ChromeService(webdriver_manager.chrome.ChromeDriverManager().install()), options=options)

    for user in tqdm(_data, desc="get phpsessid from login data file"):
        _phpsessid: str = login_and_get_cookie(driver, user, open_close=False).get("PHPSESSID").get("value")
        _jwt_token = get_bearer_token(driver)
        result_with_phpsessid.append(
            UserPHPSESSID(
                user=user,
                phpsessid=_phpsessid,
                jwt=_jwt_token
            ).for_json()
        )

        file.seek(0)
        file.write(
            f"LIST_OF_ACTUAL_LOGIN_DATAS={json.dumps(result_with_phpsessid)}" + "\n"
        )

    os.environ["LIST_OF_ACTUAL_LOGIN_DATAS"] = f"{json.dumps(result_with_phpsessid)}"

    driver.quit()


def get_login_datas_from_list(_data: list[User], path_to_output: Path, _path_to_chromedriver: str):
    if _path_to_chromedriver is not None:
        _get_login_datas_from_list(_data, path_to_output, _path_to_chromedriver)
        return

    docker = SeleniumStandaloneContainerRunner()

    docker.run_container()

    webdriver_path = docker.get_webdriver_address()

    try:
        _get_login_datas_from_list(_data, path_to_output, webdriver_path)
    finally:
        docker.kill_container()



def update_login_datas_list(_data: list[dict], path_to_output: Path, _path_to_chromedriver: str):
    with open(path_to_output / ".env.secret") as file:
        list_with_updated_phpsessid = json.loads(file.read().strip("LIST_OF_ACTUAL_LOGIN_DATAS="))


    # xuyovi ktor. poxil arajin herdin
    for _raw_user in tqdm(_data, desc="update phpsessid on env and env-file"):
        # {'username': 'parsyansuren@gmail.com', 'password': 'qwerty7890', 'PHPSESSID': 'OK', 'BEARER_TOKEN': 'invalid', 'REFRESH_TOKEN': 'OK'}
        user = User(_raw_user.get("username"), _raw_user.get("password"))
        phpsessid = _raw_user.get("PHPSESSID")
        jwt_token = {
            "skyAuthToken": _raw_user.get("BEARER_TOKEN"),
            "skyRefreshToken": _raw_user.get("REFRESH_TOKEN")
        }

        if _raw_user.get("PHPSESSID") == "invalid":
            options = webdriver.ChromeOptions()
            # options.add_argument('--ignore-ssl-errors=yes')
            # options.add_argument('--ignore-certificate-errors')
            # options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

            driver = webdriver.Remote(_path_to_chromedriver, options=options)

            _phpsessid: str = login_and_get_cookie(driver, user, open_close=False).get("PHPSESSID").get("value")
            driver.quit()

        if _raw_user.get("BEARER_TOKEN") == "invalid":
            _jwt_token = API().get_bearer_token(_raw_user.get("REFRESH_TOKEN"))

            jwt_token["skyAuthToken"] = _jwt_token.get("token")
            jwt_token["skyRefreshToken"] = _jwt_token.get("refresh_token")

        for item in list_with_updated_phpsessid:
            if {
                "username": user.username, "password": user.password
            } == {
                "username": item["username"], "password": item["password"]
            }:
                list_with_updated_phpsessid[
                    list_with_updated_phpsessid.index(item)
                ] = UserPHPSESSID(
                    user=user,
                    phpsessid=phpsessid,
                    jwt=jwt_token
                ).for_json()
                break

        with open(path_to_output / ".env.secret", "w+") as file:
            file.seek(0)
            file.write(
                f"LIST_OF_ACTUAL_LOGIN_DATAS={json.dumps(list_with_updated_phpsessid)}"
            )

    os.environ["LIST_OF_ACTUAL_LOGIN_DATAS"] = f"{json.dumps(list_with_updated_phpsessid)}"



if __name__ == '__main__':
    get_login_datas_from_list([
        User(_raw_user.get("username"), _raw_user.get("password"))

        for _raw_user in
        json.loads(open("/home/suren/Projects/upwork/maroz/parser_and_search/resources/data/data_to_login.json").read())
    ], Path("/home/suren/Projects/upwork/maroz/parser_and_search/resources/data"), "http://172.17.0.2:4444/wd/hub")


# Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE3MTMyMjk2NDgsImV4cCI6MTcxMzIzMzI0OCwicm9sZXMiOlsiUk9MRV9VU0VSIl0sImVtYWlsIjoicGFyc3lhbnN1cmVuQGdtYWlsLmNvbSJ9.EfmN_gMDJrpgyv2lyt2iHdEBN3ZXbBevTDudC_gJSpp2ioF82gbqlmseCtzoIRe3sJYQQxCtKzlH0hZHsfhRemvgCTMqvinAcnCrSn2GHOykqx1TVC5gsciJL-Eo8X2hPsMHkk9kamR_mwYW-aAU1ePDRqkIyy1Zc6REZyWV8uxrqsEtq9zVQStDyAj9ztiDlNxZK17Hxjj-u3coHWapjgNRad2E9-HCa5nLOmRyqfXUE0fvewYECqsMko7BmnPr44j22EKlwzVedNC08JHWBCkChLHdqrMkZ2uXoEoidLCy6W7YELNRUMNNNdPQl36Qn7PH7Eb0gjYl4v8QI7VE9MUyhQ-hgTM1PRxW08MBxwnhMofP7FSl6TvGPRQXZwxpo3taEdiavV0pk373GmU5jgN9RhG7SL3_0sKNmrXlx5ac83C8aW29thD8quzI0ewEJZEs0R9Xu_kRgw03xOYqZg-OuIMbbIVGJ134kloalNcvUkL6RaLOrl2L-MM_nWdOZA2MYYcz5ypXZq-QYt-nNXsCMpyzrL50k_GDzOL_4iG78vDUJcTsyHxZ28wQff4ca5DZ-TZB_Ko-JVLMeIwjdn_EWHZXlF4vWejLrhX0Pa87QlpXzzIwnd9kLc2EQ3gm1NRKHEPPplzronWwZFJ-glPgmE1HJu0sltqiNYiFRCQ
# Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE3MTMyMjk2NDgsImV4cCI6MTcxMzIzMzI0OCwicm9sZXMiOlsiUk9MRV9VU0VSIl0sImVtYWlsIjoicGFyc3lhbnN1cmVuQGdtYWlsLmNvbSJ9 | .EfmN_gMDJrpgyv2lyt2iHdEBN3ZXbBevTDudC_gJSpp2ioF82gbqlmseCtzoIRe3sJYQQxCtKzlH0hZHsfhRemvgCTMqvinAcnCrSn2GHOykqx1TVC5gsciJL-Eo8X2hPsMHkk9kamR_mwYW-aAU1ePDRqkIyy1Zc6REZyWV8uxrqsEtq9zVQStDyAj9ztiDlNxZK17Hxjj-u3coHWapjgNRad2E9-HCa5nLOmRyqfXUE0fvewYECqsMko7BmnPr44j22EKlwzVedNC08JHWBCkChLHdqrMkZ2uXoEoidLCy6W7YELNRUMNNNdPQl36Qn7PH7Eb0gjYl4v8QI7VE9MUyhQ-hgTM1PRxW08MBxwnhMofP7FSl6TvGPRQXZwxpo3taEdiavV0pk373GmU5jgN9RhG7SL3_0sKNmrXlx5ac83C8aW29thD8quzI0ewEJZEs0R9Xu_kRgw03xOYqZg-OuIMbbIVGJ134kloalNcvUkL6RaLOrl2L-MM_nWdOZA2MYYcz5ypXZq-QYt-nNXsCMpyzrL50k_GDzOL_4iG78vDUJcTsyHxZ28wQff4ca5DZ-TZB_Ko-JVLMeIwjdn_EWHZXlF4vWejLrhX0Pa87QlpXzzIwnd9kLc2EQ3gm1NRKHEPPplzronWwZFJ-glPgmE1HJu0sltqiNYiFRCQ
# Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE3MTMyMzIyMzQsImV4cCI6MTcxMzIzNTgzNCwicm9sZXMiOlsiUk9MRV9VU0VSIl0sImVtYWlsIjoicGFyc3lhbnN1cmVuQGdtYWlsLmNvbSJ9.riGdlfozK7cp5VGUJ7h5oEMMfRMUsLxykxnnnWUUOh-M5wZnlDEqxihEUphnnTxi2JbNf66_jjjj9QwJ2ju9XTrIXGjAti7OTUzUmF1CJYC7yEZpogJCxDWTzwAathpZPifyttQHoqBmICYQ1e2JoonI6tbCW8OqUNJjUNBaqsZ6jJIS7vYqhpt3cFW_ViyY-mFv39o1QKfQcBM-N5pB0-Ab2dxx6PKZqLi16mSMVPTFy1LcVNwTRTZtLomhGwP7nJw5F7a0n4opGbhmx_IZuOmLNKamYjKR9kXEfBR9PzhsamOs3y_TIuxO_wL5zekUCCEyUgKu7clXmtDeY1oEZ7MFhz5d4q6gEQTuBFJFTnNTLRVhguQg9tDIkropcUrTvbptaJ1Ipim0zNCncmsjaz2-n1Jx0vDh1mPwNM10HQWbCV9UjP4cBZyRMjTZAc-6DgKWyR2GgJnXI_BrdcgEMKe60WrDx0ULWXKDkfB_tdHMw004kMX_1MtMC1IYp4pSzj3rVtlrvWMPrj1-Ix9xPrsxcB38sutjfoc5v85MoLNHIJghLANwM6u1w_isFOv1PbHzVST0e8dId806tsljW0sdF0OXJtCQuzQ2mX_IdBsQfvg3aQu4jumpATGH6h_T3Bk3P4Nho4qtBAFR3XVs_3VSjGW-swYTxlfbNrXDmR0
