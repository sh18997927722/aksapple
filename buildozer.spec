[app]

# 应用标题
source.dir = .
title = 2026世界杯追踪器
# 包名（小写+数字+下划线，不能以数字开头）
package.name = worldcup2026

# 应用域名（通常与包名相关，用于生成完整包名）
package.domain = com.worldcup

# 应用完整包名（org.example.myapp）
full.package.name = com.worldcup.tracker2026

# 主入口模块（不含 .py 后缀）
source.include_exts = py,png,jpg,kv,atlas,ttf,json

# 主入口源文件
mainmodule = worldcup_kivy

# 入口文件（不含 .py 后缀）
mainentrypoint = worldcup_kivy.py

# Android 最低支持版本
android.minapi = 21

# 目标 API 等级
android.api = 33

# 支持的 Android 架构（armeabi-v7a + arm64-v8a 覆盖主流手机）
p4a_api = 33

# 是否支持 Google Play
android.playstore_membership = 0

# 日志级别
log_level = 2

# 打包模式
warn_on_root = 0

# buildozer 版本
buildozer.version = 1.5.0

[buildozer]

# 构建时显示完整日志
verbose = 2

# ============================================================
# Android 特定配置
# ============================================================
[android]

# 权限（必须含 INTERNET 才能联网拉取比分）
android.permissions = INTERNET, ACCESS_NETWORK_STATE, ACCESS_WIFI_STATE

# 屏幕方向: portrait（竖屏）/ landscape（横屏）/ all（全屏旋转）
orientation = portrait

# 全屏沉浸模式（隐藏状态栏）
android.fullscreen = 1

# 状态栏颜色（深色主题）
android.statusbar.color = #0d1117
android.navigationbar.color = #0d1117

# 主题: dark 或 light
android.theme = dark

# ============================================================
# Python 依赖
# ============================================================
[dependencies]

# 核心 Kivy 依赖
requirements = python3,kivy==2.2.0,urllib3,lxml,pillow

# Android 额外支持库
android.gradle_dependencies = com.google.android.material:material:1.9.0

# ============================================================
# 字体（Android 中文支持）
# ============================================================
[package]

# 使用系统内置字体（无需额外打包）
