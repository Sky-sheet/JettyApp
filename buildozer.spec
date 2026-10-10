[app]
title = فوق‌العاده اسکله‌ها
package.name = jettyallowance
package.domain = ir.baradaran

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,db,ttf,otf
source.include_patterns = assets/*,screens/*,utils/*

version = 1.0.0

requirements = python3==3.11.9,hostpython3==3.11.9,kivy==2.3.0,kivymd==1.1.1,jdatetime,pillow,openpyxl,android,pyjnius

# مجوزهای اندروید
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,INTERNET
android.api = 33
android.minapi = 24
android.ndk_api = 24
android.acceptable_sdk_licenses = android-sdk-license,android-sdk-preview-license

# صفحه عمودی
orientation = portrait
fullscreen = 0

# بهینه‌سازی
android.allow_backup = True
p4a.extra_args = --enable-androidx
p4a.arch = arm64-v8a

# لاگ
log_level = 2
warn_on_root = 0

[buildozer]
warn_on_root = 0
