import os
import platform
import shutil

def get_system_status() -> str:
    """Returns OS and system metrics."""
    total, used, free = shutil.disk_usage("/")
    total_gb = round(total / (1024 ** 3), 2)
    used_gb = round(used / (1024 ** 3), 2)
    free_gb = round(free / (1024 ** 3), 2)

    return f"""🖥️ **Apple MLX Native Host System Status**:
- OS: {platform.system()} {platform.release()} ({platform.machine()})
- CPU Architecture: {platform.processor() or 'Apple Silicon Metal'}
- Disk Total: {total_gb} GB
- Disk Used: {used_gb} GB
- Disk Free: {free_gb} GB
"""
