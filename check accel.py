
import os, re
import subprocess


# https://docs.microsoft.com/en-us/windows/win32/wmisdk/wmic
def run_wmic_value(key, value):
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


def check_vt():
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





# https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/sc-query
def run_sc_query_run(svr):
    try:
        arr_values = \
            re.findall(
                r"\w+",
                subprocess.check_output(
                    ["sc", "query", svr]
                ).decode()
            )
        return "4" == arr_values[ arr_values.index("STATE") + 1]
    except:
        raise subprocess.CalledProcessError("execution error")


def get_cpu_vendor():
    if ("GenuineIntel" in os.environ["PROCESSOR_IDENTIFIER"]):
        return "Intel".lower()
    if ("AuthenticAMD" in os.environ["PROCESSOR_IDENTIFIER"]):
        return "AMD".lower()
    return "unknown"



# https://developer.android.com/studio/run/emulator-acceleration#accel-check
# https://docs.microsoft.com/zh-cn/xamarin/android/get-started/installation/android-emulator/hardware-acceleration

def check_accel():
    
    accel_drive_download = {
        "intel": r"https://developer.android.com/studio/run/emulator-acceleration#accel-check",
        "amd": r"https://docs.microsoft.com/zh-cn/xamarin/android/get-started/installation/android-emulator/hardware-acceleration",
    }
    
    if ("intel" == get_cpu_vendor()):
        # https://github.com/intel/haxm/releases/latest
        
        if (run_sc_query_run("intelhaxm")):
            return True
        #
        print(
            "no driver detected!\nplease download from: %s" % accel_drive_download[get_cpu_vendor()]
        )
    
    if ("amd" == get_cpu_vendor()):
        # https://github.com/google/android-emulator-hypervisor-driver-for-amd-processors/releases/latest
        
        if (run_sc_query_run("gvm")):
            return True
        #
        print(
            "no driver detected!\nplease download from: %s" % accel_drive_download[get_cpu_vendor()]
        )
    
    raise RuntimeError("unknown cpu vendor")
    


print(
    "is support VT: %s\nis support accel: %s\n" % (
        "yep." if (check_vt()) else "no.",
        "yep." if (check_accel()) else "no."
    )
)