[app]

# App name
title = AutoMailReply

# Package name
package.name = automailreply

# Package domain
package.domain = org.vinay
# Source code
source.dir = .

# Source file to launch
source.main = main.py

# Versioning
version = 1.0

# Supported orientations
orientation = portrait

# Icon path (optional)
# icon.filename = icon.png

# Permissions
android.permissions = INTERNET

# Android features (optional)
# android.features = android.hardware.usb.host

# Requirements (dependencies)
requirements = python3,kivy,requests

# Bootstrap
p4a.bootstrap = sdl2

# Minimum Android API level (21 = Android 5.0)
android.minapi = 21

# Target Android API
android.target = 31

# Entry point
fullscreen = 0

# Hide the title bar
# android.hide_title = 1

# (default is False) – whether the app should be fullscreen

# Include source files in the APK
source.include_exts = py,png,jpg,kv,atlas

# Exclude .git and __pycache__
source.exclude_dirs = tests,.git,__pycache__

# Android NDK version (comment to use latest)
android.ndk = 25b

# Architecture support
android.archs = armeabi-v7a,arm64-v8a

# Logging
log_level = 2

# Build mode
#mode = debug

# Clean build directory before build (optional)
# clean = 1

# App storage access (for future use)
# android.private_storage = true

[buildozer]

# Build directory
build_dir = ./.buildozer

# Output directory
bin_dir = ./bin

# Log file
log_level = 2

# Automatically answer yes to buildozer prompts
accept_sdk_license = True

