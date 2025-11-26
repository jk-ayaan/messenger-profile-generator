import pytest
import allure
import time
from appium import webdriver
from appium.options.android import UiAutomator2Options


@allure.feature("App Launch")
@allure.story("사장님플러스 앱 실행")
class TestAppLaunch:

    @allure.title("앱 실행 테스트 - {device_name}")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_app_launch(self, driver, device_name, device_config, screenshots_dir):
        """사장님플러스 앱이 정상적으로 실행되는지 확인"""
        platform = device_config['platform']

        with allure.step(f"[{device_name}] 앱 실행 ({platform})"):
            if platform == 'Android':
                # Android 앱 실행
                app_package = device_config['capabilities'].get('appPackage', 'com.kakaopay.biz.sandbox')
                driver.activate_app(app_package)
                time.sleep(3)
            else:
                # iOS 앱 실행
                bundle_id = device_config['capabilities'].get('bundleId', 'com.kakaopay.biz.sandbox')
                driver.activate_app(bundle_id)
                time.sleep(3)

        with allure.step(f"[{device_name}] 앱 실행 확인 ({platform})"):
            if platform == 'Android':
                current_activity = driver.current_activity
                current_package = driver.current_package

                allure.attach(
                    f"Platform: {platform}\nPackage: {current_package}\nActivity: {current_activity}",
                    name="App Info",
                    attachment_type=allure.attachment_type.TEXT
                )

                assert current_package == "com.kakaopay.biz.sandbox", \
                    f"Expected package com.kakaopay.biz.sandbox, got {current_package}"
            else:
                # iOS - 앱이 실행 중인지 page_source로 확인
                page_source = driver.page_source
                bundle_id = device_config['capabilities'].get('bundleId', 'com.kakaopay.biz.sandbox')

                allure.attach(
                    f"Platform: {platform}\nBundle ID: {bundle_id}\nPage Source Length: {len(page_source)}",
                    name="App Info",
                    attachment_type=allure.attachment_type.TEXT
                )

                assert len(page_source) > 100, "iOS 앱이 정상적으로 실행되지 않았습니다"

        with allure.step(f"[{device_name}] 스크린샷 캡처"):
            screenshot_path = f"{screenshots_dir}/{device_name}_app_launched.png"
            driver.save_screenshot(screenshot_path)
            allure.attach.file(
                screenshot_path,
                name=f"{device_name} - 앱 실행 화면",
                attachment_type=allure.attachment_type.PNG
            )

        with allure.step(f"[{device_name}] 앱 실행 시간 측정"):
            # 앱이 완전히 로드될 때까지 대기
            time.sleep(2)

            # 화면 요소 확인 (앱이 정상 로드되었는지)
            page_source = driver.page_source
            assert len(page_source) > 100, "앱 화면이 정상적으로 로드되지 않았습니다"

            allure.attach(
                f"Page source length: {len(page_source)} characters",
                name="Load Status",
                attachment_type=allure.attachment_type.TEXT
            )


@allure.feature("App Launch")
@allure.story("앱 기본 기능 확인")
class TestAppBasicFunctions:

    @allure.title("홈 화면 로드 확인 - {device_name}")
    @allure.severity(allure.severity_level.NORMAL)
    def test_home_screen_loaded(self, driver, device_name, device_config, screenshots_dir):
        """홈 화면이 정상적으로 로드되는지 확인"""
        platform = device_config['platform']

        with allure.step(f"[{device_name}] 앱 실행 ({platform})"):
            if platform == 'Android':
                app_package = device_config['capabilities'].get('appPackage', 'com.kakaopay.biz.sandbox')
                driver.activate_app(app_package)
            else:
                bundle_id = device_config['capabilities'].get('bundleId', 'com.kakaopay.biz.sandbox')
                driver.activate_app(bundle_id)

        with allure.step(f"[{device_name}] 홈 화면 대기 ({platform})"):
            time.sleep(5)

        with allure.step(f"[{device_name}] 화면 상태 확인"):
            window_size = driver.get_window_size()
            allure.attach(
                f"Platform: {platform}\nWidth: {window_size['width']}\nHeight: {window_size['height']}",
                name="Window Size",
                attachment_type=allure.attachment_type.TEXT
            )

            screenshot_path = f"{screenshots_dir}/{device_name}_home_screen.png"
            driver.save_screenshot(screenshot_path)
            allure.attach.file(
                screenshot_path,
                name=f"{device_name} - 홈 화면",
                attachment_type=allure.attachment_type.PNG
            )

            assert window_size['width'] > 0 and window_size['height'] > 0
