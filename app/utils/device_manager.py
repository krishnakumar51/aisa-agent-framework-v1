"""
Device Detection and Management Utility
Handles dynamic Android device detection and capability management
"""

import subprocess
import json
import logging
import re
import time
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class DeviceManager:
    """Manages Android device detection and capabilities"""
    
    def __init__(self):
        self.devices = []
        self.selected_device = None
        
    def check_adb_available(self) -> bool:
        """Check if ADB is available in system PATH"""
        try:
            result = subprocess.run(
                ["adb", "version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                logger.info("✅ ADB is available")
                return True
            else:
                logger.error("❌ ADB not found or not working")
                return False
        except Exception as e:
            logger.error(f"❌ ADB check failed: {str(e)}")
            return False
    
    def get_connected_devices(self) -> List[Dict[str, Any]]:
        """Get list of connected Android devices"""
        devices = []
        
        try:
            result = subprocess.run(
                ["adb", "devices", "-l"],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                
                for line in lines:
                    if line.strip() and 'device' in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            device_id = parts[0]
                            status = parts[1]
                            
                            if status == 'device':  # Only connected devices
                                # Get device info
                                device_info = self.get_device_info(device_id)
                                if device_info:
                                    devices.append(device_info)
                                    
                logger.info(f"✅ Found {len(devices)} connected Android device(s)")
                return devices
                
        except Exception as e:
            logger.error(f"❌ Failed to get connected devices: {str(e)}")
            
        return devices
    
    def get_device_info(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific device"""
        try:
            device_info = {
                "device_id": device_id,
                "device_name": "Android Device",
                "is_emulator": device_id.startswith("emulator-"),
                "api_level": None,
                "screen_resolution": None,
                "manufacturer": None,
                "model": None,
                "android_version": None,
                "capabilities": {}
            }
            
            # Get device properties
            properties = [
                ("ro.build.version.release", "android_version"),
                ("ro.build.version.sdk", "api_level"),
                ("ro.product.manufacturer", "manufacturer"),
                ("ro.product.model", "model")
            ]
            
            for prop, key in properties:
                try:
                    result = subprocess.run(
                        ["adb", "-s", device_id, "shell", "getprop", prop],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    if result.returncode == 0:
                        value = result.stdout.strip()
                        device_info[key] = value
                        
                except Exception:
                    continue
            
            # Get screen resolution
            try:
                result = subprocess.run(
                    ["adb", "-s", device_id, "shell", "wm", "size"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    match = re.search(r'(\d+)x(\d+)', result.stdout)
                    if match:
                        device_info["screen_resolution"] = f"{match.group(1)}x{match.group(2)}"
                        
            except Exception:
                pass
            
            # Set display name
            if device_info["manufacturer"] and device_info["model"]:
                device_info["device_name"] = f"{device_info['manufacturer']} {device_info['model']}"
            elif device_info["is_emulator"]:
                device_info["device_name"] = f"Android Emulator ({device_id})"
            
            # Create Appium capabilities
            device_info["capabilities"] = self.create_appium_capabilities(device_info)
            
            logger.info(f"✅ Device info retrieved: {device_info['device_name']}")
            return device_info
            
        except Exception as e:
            logger.error(f"❌ Failed to get device info for {device_id}: {str(e)}")
            return None
    
    def create_appium_capabilities(self, device_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create Appium capabilities for the device"""
        capabilities = {
            "platformName": "Android",
            "deviceName": device_info["device_name"],
            "udid": device_info["device_id"],
            "automationName": "UiAutomator2",
            "noReset": False,
            "fullReset": False,
            "newCommandTimeout": 300,
            "unicodeKeyboard": True,
            "resetKeyboard": True,
            "autoGrantPermissions": True,
            "systemPort": 8200,  # Default, can be changed if needed
            "enforceXPath1": True
        }
        
        # Add API level if available
        if device_info.get("api_level"):
            try:
                capabilities["platformVersion"] = device_info["android_version"] or device_info["api_level"]
            except:
                pass
                
        return capabilities
    
    def select_best_device(self) -> Optional[Dict[str, Any]]:
        """Select the best available device for automation"""
        devices = self.get_connected_devices()
        
        if not devices:
            logger.error("❌ No connected Android devices found")
            return None
        
        # Prefer real devices over emulators
        real_devices = [d for d in devices if not d["is_emulator"]]
        if real_devices:
            selected = real_devices[0]
        else:
            selected = devices[0]
        
        self.selected_device = selected
        logger.info(f"✅ Selected device: {selected['device_name']} ({selected['device_id']})")
        
        return selected
    
    def wait_for_device_ready(self, device_id: str, timeout: int = 30) -> bool:
        """Wait for device to be ready for automation"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Check if device is online
                result = subprocess.run(
                    ["adb", "-s", device_id, "shell", "echo", "ready"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0 and "ready" in result.stdout:
                    logger.info(f"✅ Device {device_id} is ready")
                    return True
                    
            except Exception:
                pass
                
            time.sleep(2)
            
        logger.error(f"❌ Device {device_id} not ready after {timeout} seconds")
        return False
    
    def get_appium_server_status(self) -> Dict[str, Any]:
        """Check Appium server status"""
        try:
            import requests
            
            response = requests.get("http://localhost:4723/status", timeout=5)
            
            if response.status_code == 200:
                return {
                    "running": True,
                    "status": "ready",
                    "response": response.json()
                }
            else:
                return {
                    "running": False,
                    "status": "not_ready",
                    "error": f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            return {
                "running": False,
                "status": "offline",
                "error": str(e)
            }
    
    def save_device_config(self, output_path: Path) -> bool:
        """Save device configuration for Agent 3 to use"""
        try:
            if not self.selected_device:
                self.select_best_device()
                
            if self.selected_device:
                config = {
                    "timestamp": time.time(),
                    "selected_device": self.selected_device,
                    "all_devices": self.devices,
                    "appium_server": self.get_appium_server_status()
                }
                
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                    
                logger.info(f"✅ Device config saved to: {output_path}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to save device config: {str(e)}")
            
        return False


def detect_android_devices() -> Optional[Dict[str, Any]]:
    """Quick function to detect and return best Android device"""
    device_manager = DeviceManager()
    
    if not device_manager.check_adb_available():
        return None
        
    return device_manager.select_best_device()


if __name__ == "__main__":
    # Test device detection
    logging.basicConfig(level=logging.INFO)
    
    device_manager = DeviceManager()
    
    print("🔍 Checking for Android devices...")
    
    if device_manager.check_adb_available():
        devices = device_manager.get_connected_devices()
        
        if devices:
            print(f"\n📱 Found {len(devices)} connected device(s):")
            for device in devices:
                print(f"  • {device['device_name']} ({device['device_id']})")
                print(f"    Android {device['android_version']} | API {device['api_level']}")
                print(f"    Resolution: {device['screen_resolution']}")
                
            best_device = device_manager.select_best_device()
            if best_device:
                print(f"\n✅ Best device selected: {best_device['device_name']}")
        else:
            print("❌ No connected Android devices found")
    else:
        print("❌ ADB not available")