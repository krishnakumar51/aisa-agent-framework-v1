"""
Device Manager
Production device detection and management utility with ADB integration
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
    """
    Production device manager for Android device detection and capabilities.
    Maintains all existing functionality while integrating with the framework.
    """
    
    def __init__(self):
        self.devices = []
        self.selected_device = None
        self.adb_available = None
        logger.info("🔧 Device Manager initialized")
    
    def check_adb_available(self) -> bool:
        """Check if ADB is available in system PATH"""
        if self.adb_available is not None:
            return self.adb_available
        
        try:
            result = subprocess.run(
                ["adb", "version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                logger.info("✅ ADB is available")
                self.adb_available = True
                return True
            else:
                logger.error("❌ ADB not found or not working")
                self.adb_available = False
                return False
        except Exception as e:
            logger.error(f"❌ ADB check failed: {str(e)}")
            self.adb_available = False
            return False
    
    def get_connected_devices(self) -> List[Dict[str, Any]]:
        """Get list of connected Android devices"""
        devices = []
        
        if not self.check_adb_available():
            logger.warning("⚠️ ADB not available, cannot detect devices")
            return devices
        
        try:
            result = subprocess.run(
                ["adb", "devices", "-l"],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                logger.info(f"🔍 ADB devices output: {len(lines)} lines")
                
                for line in lines[1:]:  # Skip header
                    if line.strip() and 'device' in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            device_id = parts[0]
                            device_status = parts[1]
                            
                            if device_status == "device":
                                device_info = self._get_device_info(device_id)
                                devices.append(device_info)
                                logger.info(f"✅ Found device: {device_id}")
                
                logger.info(f"📱 Total devices found: {len(devices)}")
            else:
                logger.error(f"❌ ADB devices command failed: {result.stderr}")
        
        except subprocess.TimeoutExpired:
            logger.error("❌ ADB devices command timed out")
        except Exception as e:
            logger.error(f"❌ Device detection failed: {str(e)}")
        
        self.devices = devices
        return devices
    
    def _get_device_info(self, device_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific device"""
        device_info = {
            "device_id": device_id,
            "device_name": f"Android Device ({device_id})",
            "is_emulator": device_id.startswith("emulator-"),
            "status": "available",
            "platform_version": "unknown",
            "api_level": "unknown",
            "manufacturer": "unknown",
            "model": "unknown",
            "capabilities": self._get_device_capabilities(device_id)
        }
        
        try:
            # Get device properties
            properties = self._get_device_properties(device_id)
            
            device_info.update({
                "platform_version": properties.get("ro.build.version.release", "unknown"),
                "api_level": properties.get("ro.build.version.sdk", "unknown"),
                "manufacturer": properties.get("ro.product.manufacturer", "unknown"),
                "model": properties.get("ro.product.model", "unknown"),
                "device_name": f"{properties.get('ro.product.manufacturer', 'Unknown')} {properties.get('ro.product.model', 'Device')}"
            })
            
            logger.info(f"📋 Device info collected: {device_info['device_name']}")
        
        except Exception as e:
            logger.warning(f"⚠️ Could not get detailed info for {device_id}: {str(e)}")
        
        return device_info
    
    def _get_device_properties(self, device_id: str) -> Dict[str, str]:
        """Get device properties using getprop"""
        properties = {}
        
        try:
            result = subprocess.run(
                ["adb", "-s", device_id, "shell", "getprop"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if line.strip() and ':' in line:
                        # Parse getprop output: [key]: [value]
                        match = re.match(r'\[([^\]]+)\]: \[([^\]]*)\]', line.strip())
                        if match:
                            key, value = match.groups()
                            properties[key] = value
        
        except Exception as e:
            logger.warning(f"⚠️ Could not get properties for {device_id}: {str(e)}")
        
        return properties
    
    def _get_device_capabilities(self, device_id: str) -> Dict[str, Any]:
        """Get device capabilities for Appium"""
        return {
            "platformName": "Android",
            "deviceName": device_id,
            "udid": device_id,
            "automationName": "UiAutomator2",
            "newCommandTimeout": 300,
            "noReset": True,
            "fullReset": False,
            "autoGrantPermissions": True,
            "systemPort": self._get_system_port(device_id)
        }
    
    def _get_system_port(self, device_id: str) -> int:
        """Get system port for device (to avoid conflicts)"""
        # Generate port based on device ID hash
        base_port = 8200
        device_hash = hash(device_id) % 1000
        return base_port + device_hash
    
    def select_device(self, device_id: str = None) -> Dict[str, Any]:
        """Select device for automation"""
        if not self.devices:
            self.get_connected_devices()
        
        if not self.devices:
            return {
                "success": False,
                "error": "No devices available",
                "selected_device": None
            }
        
        # Auto-select first device if none specified
        if device_id is None:
            self.selected_device = self.devices[0]
            logger.info(f"🎯 Auto-selected device: {self.selected_device['device_id']}")
        else:
            # Find specified device
            for device in self.devices:
                if device["device_id"] == device_id:
                    self.selected_device = device
                    logger.info(f"🎯 Selected device: {device_id}")
                    break
            else:
                return {
                    "success": False,
                    "error": f"Device {device_id} not found",
                    "available_devices": [d["device_id"] for d in self.devices]
                }
        
        return {
            "success": True,
            "selected_device": self.selected_device,
            "device_capabilities": self.selected_device["capabilities"]
        }
    
    def get_device_status(self, device_id: str = None) -> Dict[str, Any]:
        """Get current status of specific device"""
        target_device_id = device_id or (self.selected_device["device_id"] if self.selected_device else None)
        
        if not target_device_id:
            return {
                "success": False,
                "error": "No device specified or selected"
            }
        
        try:
            # Check if device is still connected
            result = subprocess.run(
                ["adb", "-s", target_device_id, "shell", "echo", "test"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "device_id": target_device_id,
                    "status": "connected",
                    "responsive": True
                }
            else:
                return {
                    "success": False,
                    "device_id": target_device_id,
                    "status": "disconnected",
                    "responsive": False
                }
        
        except Exception as e:
            return {
                "success": False,
                "device_id": target_device_id,
                "status": "error",
                "error": str(e)
            }
    
    def install_app(self, apk_path: str, device_id: str = None) -> Dict[str, Any]:
        """Install APK on selected device"""
        target_device_id = device_id or (self.selected_device["device_id"] if self.selected_device else None)
        
        if not target_device_id:
            return {
                "success": False,
                "error": "No device specified or selected"
            }
        
        if not Path(apk_path).exists():
            return {
                "success": False,
                "error": f"APK file not found: {apk_path}"
            }
        
        try:
            result = subprocess.run(
                ["adb", "-s", target_device_id, "install", "-r", apk_path],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0 and "Success" in result.stdout:
                logger.info(f"✅ App installed successfully on {target_device_id}")
                return {
                    "success": True,
                    "device_id": target_device_id,
                    "apk_path": apk_path,
                    "install_output": result.stdout
                }
            else:
                logger.error(f"❌ App installation failed: {result.stderr}")
                return {
                    "success": False,
                    "device_id": target_device_id,
                    "error": result.stderr,
                    "install_output": result.stdout
                }
        
        except Exception as e:
            logger.error(f"❌ App installation error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_installed_packages(self, device_id: str = None) -> List[str]:
        """Get list of installed packages"""
        target_device_id = device_id or (self.selected_device["device_id"] if self.selected_device else None)
        
        if not target_device_id:
            return []
        
        try:
            result = subprocess.run(
                ["adb", "-s", target_device_id, "shell", "pm", "list", "packages"],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0:
                packages = []
                for line in result.stdout.split('\n'):
                    if line.strip() and line.startswith('package:'):
                        package_name = line.replace('package:', '').strip()
                        packages.append(package_name)
                
                logger.info(f"📦 Found {len(packages)} installed packages")
                return packages
        
        except Exception as e:
            logger.warning(f"⚠️ Could not get installed packages: {str(e)}")
        
        return []
    
    def start_app(self, package_name: str, activity_name: str = None, device_id: str = None) -> Dict[str, Any]:
        """Start app on device"""
        target_device_id = device_id or (self.selected_device["device_id"] if self.selected_device else None)
        
        if not target_device_id:
            return {
                "success": False,
                "error": "No device specified or selected"
            }
        
        try:
            if activity_name:
                component = f"{package_name}/{activity_name}"
            else:
                component = package_name
            
            result = subprocess.run(
                ["adb", "-s", target_device_id, "shell", "am", "start", "-n", component],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                logger.info(f"🚀 App started: {package_name}")
                return {
                    "success": True,
                    "device_id": target_device_id,
                    "package_name": package_name,
                    "activity_name": activity_name
                }
            else:
                logger.error(f"❌ App start failed: {result.stderr}")
                return {
                    "success": False,
                    "error": result.stderr
                }
        
        except Exception as e:
            logger.error(f"❌ App start error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        return {
            "adb_available": self.check_adb_available(),
            "connected_devices": len(self.devices),
            "selected_device": self.selected_device["device_id"] if self.selected_device else None,
            "device_manager": "production",
            "capabilities": [
                "device_detection",
                "device_properties",
                "app_installation",
                "package_management",
                "device_status_monitoring"
            ]
        }
    
    def refresh_devices(self) -> List[Dict[str, Any]]:
        """Refresh device list"""
        logger.info("🔄 Refreshing device list...")
        self.devices = []
        self.adb_available = None  # Force re-check
        return self.get_connected_devices()

# Global device manager instance
_device_manager = None

def get_device_manager() -> DeviceManager:
    """Get global device manager instance"""
    global _device_manager
    if _device_manager is None:
        _device_manager = DeviceManager()
    return _device_manager

if __name__ == "__main__":
    # Test device manager
    def test_device_manager():
        print("🧪 Testing Device Manager...")
        
        dm = DeviceManager()
        
        # Test ADB availability
        adb_available = dm.check_adb_available()
        print(f"✅ ADB available: {adb_available}")
        
        if adb_available:
            # Test device detection
            devices = dm.get_connected_devices()
            print(f"✅ Devices found: {len(devices)}")
            
            if devices:
                # Test device selection
                selection_result = dm.select_device()
                print(f"✅ Device selected: {selection_result['success']}")
                
                if selection_result["success"]:
                    # Test device status
                    status = dm.get_device_status()
                    print(f"✅ Device status: {status['status']}")
                    
                    # Test installed packages
                    packages = dm.get_installed_packages()
                    print(f"✅ Installed packages: {len(packages)}")
        
        # Test system info
        system_info = dm.get_system_info()
        print(f"✅ System info: {system_info['device_manager']}")
        
        print("🎉 Device Manager test completed!")
    
    test_device_manager()