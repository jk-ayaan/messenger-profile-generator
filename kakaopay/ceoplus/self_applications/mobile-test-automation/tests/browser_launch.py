import time
from typing import Dict
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.common.appiumby import AppiumBy


class BrowserLaunchTest:
    def __init__(self, driver, device_name: str):
        self.driver = driver
        self.device_name = device_name
        self.target_url = "https://sandbox-biz-int.kakaopay.com/applications"
    
    def run_test(self) -> Dict[str, any]:
        result = {
            'device': self.device_name,
            'status': 'FAILED',
            'url': self.target_url,
            'error': None,
            'load_time': None
        }
        
        try:
            print(f"[{self.device_name}] Starting browser launch test...")
            start_time = time.time()
            
            print(f"[{self.device_name}] Navigating to {self.target_url}")
            self.driver.get(self.target_url)
            
            wait = WebDriverWait(self.driver, 30)
            
            try:
                wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
            except:
                pass
            
            load_time = time.time() - start_time
            result['load_time'] = round(load_time, 2)
            
            print(f"[{self.device_name}] Page loaded in {result['load_time']} seconds")
            
            current_url = self.driver.current_url
            print(f"[{self.device_name}] Current URL: {current_url}")
            
            time.sleep(3)
            
            page_title = self.driver.title
            print(f"[{self.device_name}] Page title: {page_title}")
            
            screenshot_path = f"screenshots/{self.device_name}_browser_test.png"
            self.driver.save_screenshot(screenshot_path)
            print(f"[{self.device_name}] Screenshot saved to {screenshot_path}")
            
            result['status'] = 'PASSED'
            result['page_title'] = page_title
            result['final_url'] = current_url
            
            print(f"[{self.device_name}] Test completed successfully!")
            
        except Exception as e:
            result['error'] = str(e)
            print(f"[{self.device_name}] Test failed with error: {str(e)}")
            
            try:
                error_screenshot = f"screenshots/{self.device_name}_error.png"
                self.driver.save_screenshot(error_screenshot)
                print(f"[{self.device_name}] Error screenshot saved to {error_screenshot}")
            except:
                pass
        
        return result
    
    def verify_page_loaded(self) -> bool:
        try:
            WebDriverWait(self.driver, 10).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            return True
        except:
            return False