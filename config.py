"""
Configuration settings for the Remote Patient Monitoring application
"""

# API endpoint
BASE_URL = "https://disp.yxl.ch/rpm/patients/{}"

# Valid patient IDs
VALID_PATIENTS = [1, 2, 3, 10, 42]

# SpO2 threshold for warnings
SPO2_THRESHOLD = 95
