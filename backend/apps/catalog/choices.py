"""Bộ giá trị dùng chung giữa tin tuyển dụng (jobs) và hồ sơ ứng viên (candidates).

Đặt ở catalog để hai app ngang hàng không phải import lẫn nhau.
"""
from django.db import models


class JobType(models.TextChoices):
    FULL_TIME = 'full_time', 'Toàn thời gian'
    PART_TIME = 'part_time', 'Bán thời gian'
    INTERNSHIP = 'internship', 'Thực tập'
    CONTRACT = 'contract', 'Hợp đồng'
    FREELANCE = 'freelance', 'Freelance'


class WorkMode(models.TextChoices):
    ONSITE = 'onsite', 'Tại văn phòng'
    REMOTE = 'remote', 'Từ xa'
    HYBRID = 'hybrid', 'Linh hoạt (hybrid)'


class JobLevel(models.TextChoices):
    INTERN = 'intern', 'Thực tập sinh'
    FRESHER = 'fresher', 'Fresher'
    JUNIOR = 'junior', 'Junior'
    MIDDLE = 'middle', 'Middle'
    SENIOR = 'senior', 'Senior'
    LEAD = 'lead', 'Trưởng nhóm'
    MANAGER = 'manager', 'Quản lý'
