
import os, re
import subprocess


# https://docs.microsoft.com/en-us/windows/win32/wmisdk/wmic
def run_wmic_value(key, value):
    try:
        return \
            subprocess.check_output(
                ["wmic", key, "get", value, "/VALUE"]
            ).decode().strip().split("=")[1]
    except:
        return ''
        raise subprocess.CalledProcessError("execution error")


# https://docs.microsoft.com/en-us/windows/win32/cimwin32prov/win32-processor

# https://docs.microsoft.com/en-us/windows/win32/cimwin32prov/win32-operatingsystem

def get_os_version():
    # wmic os get Version
    return run_wmic_value("os", "Version")

def get_os_bit():
    # wmic os get OSArchitecture
    # wmic cpu get AddressWidth
    return run_wmic_value("cpu", "AddressWidth")

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
    return const_arr_arch.get(run_wmic_value("cpu", "Architecture"), "unknown")

def support_vt():
	# wmic cpu get VirtualizationFirmwareEnabled
    return "TRUE" == run_wmic_value("cpu", "VirtualizationFirmwareEnabled").upper()


def check_vt():
    # wmic os get DataExecutionPrevention_Available
    dep = "TRUE" == run_wmic_value("os", "DataExecutionPrevention_Available").upper()
    
    # wmic cpu get SecondLevelAddressTranslationExtensions
    slat = "TRUE" == run_wmic_value("cpu", "SecondLevelAddressTranslationExtensions").upper()
    
	# wmic cpu get VMMonitorModeExtensions
    vmmme = "TRUE" == run_wmic_value("cpu", "VMMonitorModeExtensions").upper()
    
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
        return False
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
    
    accel_drive = {
        "intel": 
            (
                "intelhaxm",
                r"https://github.com/intel/haxm/releases/latest",
            ),
        
        "amd": 
            (
                "gvm",
                r"https://github.com/google/android-emulator-hypervisor-driver-for-amd-processors/releases/latest",
            ),
    }
    
    if (get_cpu_vendor() in accel_drive):
        info = accel_drive[ get_cpu_vendor() ]
        if (run_sc_query_run(info[0])):
            return True
        else:
            print(
                "\nno driver detected!\nplease download from: %s\n\n" % info[1]
            )
            return False
        
    raise RuntimeError("unknown cpu vendor")
    

print(
    "is support VT: %s\nis support accel: %s\n" % (
        "yep." if (check_vt()) else "no.",
        "yep." if (check_accel()) else "no."
    )
)