import pytest
import json
import os
import subprocess
import time
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions


def load_devices():
    """Load device configurations from JSON file"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config/devices.json')
    with open(config_path, 'r') as f:
        data = json.load(f)
    return data['devices']


def get_connected_android_devices():
    """Get list of currently connected Android device UDIDs"""
    result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
    lines = result.stdout.strip().split('\n')[1:]
    connected = []
    for line in lines:
        if line.strip() and 'device' in line and 'offline' not in line:
            udid = line.split()[0]
            connected.append(udid)
    return connected


def get_connected_ios_devices():
    """Get list of currently connected iOS device UDIDs"""
    connected = []
    try:
        result = subprocess.run(
            ['xcrun', 'xctrace', 'list', 'devices'],
            capture_output=True, text=True
        )
        lines = result.stdout.strip().split('\n')
        for line in lines:
            if ('iPhone' in line or 'iPad' in line) and 'Simulator' not in line:
                # Extract UDID from parentheses at the end
                if '(' in line:
                    parts = line.split('(')
                    if len(parts) >= 2:
                        udid = parts[-1].rstrip(')')
                        if len(udid) > 20:  # Real device UDIDs are long
                            connected.append(udid)
    except Exception as e:
        print(f"Error getting iOS devices: {e}")
    return connected


def get_all_connected_devices():
    """Get all connected device UDIDs (Android + iOS)"""
    android_devices = get_connected_android_devices()
    ios_devices = get_connected_ios_devices()
    return android_devices + ios_devices


@pytest.fixture(scope="session")
def screenshots_dir():
    """Create and return screenshots directory"""
    dir_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'screenshots')
    os.makedirs(dir_path, exist_ok=True)
    return dir_path


@pytest.fixture(scope="session")
def allure_results_dir():
    """Create and return allure results directory"""
    dir_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'allure-results')
    os.makedirs(dir_path, exist_ok=True)
    return dir_path


def pytest_generate_tests(metafunc):
    """Generate test instances for each connected device"""
    if "driver" in metafunc.fixturenames and "device_name" in metafunc.fixturenames:
        devices = load_devices()
        connected_udids = get_all_connected_devices()

        print(f"\nConnected device UDIDs: {connected_udids}")

        # Filter to only connected devices
        available_devices = [d for d in devices if d['capabilities']['udid'] in connected_udids]

        print(f"Available devices for testing: {[d['name'] for d in available_devices]}")

        if available_devices:
            metafunc.parametrize(
                "device_config",
                available_devices,
                ids=[d['name'] for d in available_devices],
                indirect=True
            )


@pytest.fixture(scope="function")
def device_config(request):
    """Return device configuration"""
    return request.param


@pytest.fixture(scope="function")
def device_name(device_config):
    """Return device name"""
    return device_config['name']


@pytest.fixture(scope="function")
def driver(device_config, request):
    """Create Appium driver for the device"""
    capabilities = device_config['capabilities']
    port = device_config['appium_port']
    device_name = device_config['name']
    platform = device_config['platform']

    print(f"\n[{device_name}] Creating driver on port {port} for {platform}...")

    if platform == 'iOS':
        options = XCUITestOptions()
    else:
        options = UiAutomator2Options()

    for key, value in capabilities.items():
        options.set_capability(key, value)

    driver = webdriver.Remote(
        f'http://localhost:{port}',
        options=options
    )

    print(f"[{device_name}] Driver created successfully")

    yield driver

    print(f"[{device_name}] Closing driver...")
    driver.quit()


def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "device(name): mark test to run on specific device"
    )
