
import subprocess

def run_wmic_value(key, value):
    # https://docs.microsoft.com/en-us/windows/win32/wmisdk/wmic
    try:
        return \
            subprocess.check_output(
                ["wmic", key, "get", value, "/VALUE"]
            ).decode().strip().split("=")
    except:
        raise subprocess.CalledProcessError("execution error")


# https://docs.microsoft.com/en-us/windows/win32/cimwin32prov/win32-processor

# https://docs.microsoft.com/en-us/windows/win32/cimwin32prov/win32-operatingsystem

def get_os_version():
    # wmic os get Version
    values = run_wmic_value("os", "Version")
    return values[1]

def get_os_bit():
    # wmic os get OSArchitecture
    values = run_wmic_value("os", "OSArchitecture")
    return values[1][:2]

def get_arch():
    # wmic cpu get Architecture
    const_arr_arch = {
        "0": "x86",
        "1": "MIPS",
        "2": "Alpha",
        "3": "PowerPC",
        "5": "ARM",
        "6": "ia64",
        "9": "x64",
    }
    values = run_wmic_value("cpu", "Architecture")
    return const_arr_arch.get(values[1], "unknown")

def support_vt():
	# wmic cpu get VirtualizationFirmwareEnabled
    values = run_wmic_value("cpu", "VirtualizationFirmwareEnabled")
    return "TRUE" == values[1].upper()



# https://docs.microsoft.com/zh-cn/xamarin/android/get-started/installation/android-emulator/hardware-acceleration

def check_accel():
    
    # wmic os get DataExecutionPrevention_Available
    # wmic cpu get SecondLevelAddressTranslationExtensions
	# wmic cpu get VMMonitorModeExtensions
    values = run_wmic_value("os", "DataExecutionPrevention_Available")
    dep = "TRUE" == values[1].upper()
    
    values = run_wmic_value("cpu", "SecondLevelAddressTranslationExtensions")
    slat = "TRUE" == values[1].upper()
    
    values = run_wmic_value("cpu", "VMMonitorModeExtensions")
    vmmme = "TRUE" == values[1].upper()
    
    return get_os_version().startswith("10.") \
        and "x64" == get_arch() \
        and "64" == get_os_bit() \
        and support_vt() \
        and dep and slat and vmmme


print(
    "is support VT accel: %s" % "yep." if (check_accel()) else "no."
)