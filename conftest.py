import logging
from os.path import dirname, abspath
from os import getenv

import allure
import pytest
from faker import Faker
from selenium import webdriver
from selenium.webdriver.edge.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

LOGGER = logging.getLogger(__name__)
ROOT_DIR = dirname(abspath(__file__))
DOWNLOAD_DIR = ROOT_DIR + "\\download_files"

@pytest.fixture(scope="session")
def get_driver(request):
    jenkins = getenv('JENKINS_HOME')
    browser_list = request.config.getoption("--browser")

    if 'chrome' in browser_list:
        options = webdriver.ChromeOptions()
        preferences = {"download.default_directory": DOWNLOAD_DIR}
        options.add_argument("--start-maximized")
        options.add_experimental_option("prefs", preferences)
        capabilities = options.to_capabilities()
        if jenkins:
            options.add_argument('--headless')
            options.add_argument("--window-size=1920,1080")
        try:
            driver = webdriver.Chrome(ChromeDriverManager().install(), desired_capabilities=capabilities)
        except:
            driver = webdriver.Chrome(executable_path="C:/Users/artem.stolbtsov/.wdm/drivers/chromedriver/80.0.3987.16/win32/chromedriver.exe", desired_capabilities=capabilities)
    elif 'firefox' in browser_list:
        fp = webdriver.FirefoxProfile()
        fp.set_preference("browser.download.folderList", 2)
        fp.set_preference("browser.download.manager.showWhenStarting", False)
        fp.set_preference('browser.download.dir', DOWNLOAD_DIR)
        fp.set_preference("browser.helperApps.alwaysAsk.force", False)
        fp.set_preference("plugin.disable_full_page_plugin_for_types", "application/pdf")
        fp.set_preference("browser.helperApps.neverAsk.saveToDisk", 'application/pdf,application/x-pdf')
        fp.set_preference("pdfjs.disabled", True)
        driver = webdriver.Firefox(executable_path=GeckoDriverManager().install(), firefox_profile=fp)
    elif 'edge' in browser_list:
        driver: WebDriver = webdriver.Edge()
    LOGGER.info('Test run with *{0}* browser.'.format(browser_list))
    yield driver
    driver.quit()


def pytest_addoption(parser):
    parser.addoption("--browser", action="store", default="chrome", help="Type of browser: edge, chrome, firefox")



@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item):
    outcome = yield
    rep = outcome.get_result()
    marker = item.get_closest_marker("ui")
    if marker:
        if rep.when == "call" and rep.failed:
            try:
                allure.attach(item.instance.driver.get_screenshot_as_png(),
                              name=item.name,
                              attachment_type=allure.attachment_type.PNG)
            except Exception as e:
                print(e)

@pytest.fixture()
def faker():
    return Faker()

@pytest.fixture(scope="function")
def browser():
    print("\nstart browser for test..")
    driver = webdriver.Chrome(executable_path="C:/Users/artem.stolbtsov/.wdm/drivers/chromedriver/80.0.3987.16/win32/chromedriver.exe")
    yield driver
    print("\nquit browser..")
    driver.quit()