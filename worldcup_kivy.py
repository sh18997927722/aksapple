#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2026 FIFA World Cup Tracker — Kivy 安卓版 v1.0
移植自 PyQt5 桌面版 worldcup.py

功能:
  - Tab1 赛程: 按日期分组展示72场小组赛
  - Tab2 积分: 12组小组积分榜
  - Tab3 第三名: 各组第三名横向排位
  - 深色主题，竖屏手机友好
  - 国旗 emoji，数据来自球迷屋 qiumiwu.com

依赖: kivy, urllib3, lxml (buildozer.spec 中声明)
"""

import sys
import os
import json
import threading
from datetime import datetime

# Kivy 必须在 import 其他 Kivy 模块前配置
from kivy.config import Config
Config.set('kivy', 'orientation', 'portrait')
Config.set('kivy', 'keyboard_mode', 'system')

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.utils import get_color_from_hex as gch
from kivy.graphics import Color, Rectangle
from kivy.properties import BooleanProperty, StringProperty, ListProperty
from kivy.clock import Clock

# ============================================================
# 颜色常量 — 深色主题（手机 AMOLED 友好）
# ============================================================
C_BG          = "#0d1117"   # 页面背景
C_CARD        = "#161b22"   # 卡片背景
C_CARD_ALT    = "#1c2128"   # 交替行
C_BORDER      = "#30363d"   # 边框线
C_BLUE        = "#58a6ff"   # 主题蓝
C_BLUE_DARK   = "#1f6feb"   # 深蓝
C_TEXT        = "#e6edf3"   # 主文字
C_TEXT_SEC    = "#8b949e"   # 次要文字
C_GREEN       = "#3fb950"   # 绿色（胜/晋级）
C_RED         = "#f85149"   # 红色（负/淘汰）
C_ORANGE      = "#d29922"   # 橙色（平局/待定）
C_YELLOW      = "#e3b341"   # 黄色
C_HEADER_BG   = "#21262d"   # 表头背景
C_DATE_HDR    = "#2d333b"   # 日期标题栏
C_GREEN_LIGHT = "#0d3320"   # 晋级行高亮
C_ORANGE_LIGHT= "#3d2200"   # 边缘行高亮
C_WHITE       = "#ffffff"
C_TEAM_WIN    = "#56d364"   # 赢球队高亮

# ============================================================
# 数据定义 — 与 worldcup.py 完全一致
# ============================================================
GROUPS = {
    "A": ["墨西哥", "南非", "韩国", "捷克"],
    "B": ["加拿大", "波黑", "卡塔尔", "瑞士"],
    "C": ["巴西", "摩洛哥", "海地", "苏格兰"],
    "D": ["美国", "巴拉圭", "澳大利亚", "土耳其"],
    "E": ["德国", "库拉索", "科特迪瓦", "厄瓜多尔"],
    "F": ["荷兰", "日本", "瑞典", "突尼斯"],
    "G": ["比利时", "埃及", "伊朗", "新西兰"],
    "H": ["西班牙", "佛得角", "沙特阿拉伯", "乌拉圭"],
    "I": ["法国", "塞内加尔", "伊拉克", "挪威"],
    "J": ["阿根廷", "阿尔及利亚", "奥地利", "约旦"],
    "K": ["葡萄牙", "民主刚果", "乌兹别克斯坦", "哥伦比亚"],
    "L": ["英格兰", "克罗地亚", "加纳", "巴拿马"],
}

FLAGS = {
    "墨西哥": "\U0001f1f2\U0001f1fd", "南非": "\U0001f1ff\U0001f1e6",
    "韩国": "\U0001f1f0\U0001f1f7", "捷克": "\U0001f1e8\U0001f1ff",
    "加拿大": "\U0001f1e8\U0001f1e6", "波黑": "\U0001f1e7\U0001f1ea",
    "卡塔尔": "\U0001f1f6\U0001f1e6", "瑞士": "\U0001f1e8\U0001f1ed",
    "巴西": "\U0001f1e7\U0001f1f7", "摩洛哥": "\U0001f1f2\U0001f1e6",
    "海地": "\U0001f1ed\U0001f1f9", "苏格兰": "\U0001f1ec\U0001f1ec",
    "美国": "\U0001f1fa\U0001f1f8", "巴拉圭": "\U0001f1f5\U0001f1fe",
    "澳大利亚": "\U0001f1e6\U0001f1fa", "土耳其": "\U0001f1f9\U0001f1f7",
    "德国": "\U0001f1e9\U0001f1ea", "科特迪瓦": "\U0001f1e8\U0001f1ee",
    "厄瓜多尔": "\U0001f1ea\U0001f1e8", "库拉索": "\U0001f1e8\U0001f1fc",
    "瑞典": "\U0001f1f8\U0001f1ea", "日本": "\U0001f1ef\U0001f1f5",
    "荷兰": "\U0001f1f3\U0001f1f1", "突尼斯": "\U0001f1f9\U0001f1f3",
    "新西兰": "\U0001f1f3\U0001f1ff", "伊朗": "\U0001f1ee\U0001f1f7",
    "哥伦比亚": "\U0001f1e8\U0001f1f4", "乌兹别克斯坦": "\U0001f1fa\U0001f1ff",
    "乌拉圭": "\U0001f1fa\U0001f1fe", "沙特阿拉伯": "\U0001f1f8\U0001f1e6",
    "民主刚果": "\U0001f1e9\U0001f1ec", "奥地利": "\U0001f1e6\U0001f1f9",
    "挪威": "\U0001f1f3\U0001f1f4", "法国": "\U0001f1eb\U0001f1f7",
    "克罗地亚": "\U0001f1ed\U0001f1f7", "阿根廷": "\U0001f1e6\U0001f1f7",
    "比利时": "\U0001f1e7\U0001f1ea", "加纳": "\U0001f1ec\U0001f1ed",
    "伊拉克": "\U0001f1ee\U0001f1f6", "塞内加尔": "\U0001f1f8\U0001f1f3",
    "英格兰": "\U0001f1ec\U0001f1ea", "西班牙": "\U0001f1ea\U0001f1f8",
    "佛得角": "\U0001f1e8\U0001f1fb", "阿尔及利亚": "\U0001f1e9\U0001f1e6",
    "葡萄牙": "\U0001f1f5\U0001f1f9",
}

WEEKDAY_MAP = {0: "周一", 1: "周二", 2: "周三", 3: "周四", 4: "周五", 5: "周六", 6: "周日"}

# 72场完整比赛数据 (group, round, month, day, hour, minute, home, away, home_score, away_score, status)
ALL_MATCHES = [
    # === 第1轮 ===
    ("A", 1, 6, 12,  3,  0, "墨西哥", "南非", 2, 0, "FT"),
    ("A", 1, 6, 12, 10,  0, "韩国", "捷克", 2, 1, "FT"),
    ("B", 1, 6, 13,  3,  0, "加拿大", "波黑", 1, 1, "FT"),
    ("B", 1, 6, 14,  3,  0, "卡塔尔", "瑞士", 1, 1, "FT"),
    ("C", 1, 6, 14,  6,  0, "巴西", "摩洛哥", 1, 1, "FT"),
    ("C", 1, 6, 14,  9,  0, "海地", "苏格兰", 0, 1, "FT"),
    ("D", 1, 6, 13,  9,  0, "美国", "巴拉圭", 4, 1, "FT"),
    ("D", 1, 6, 14, 12,  0, "澳大利亚", "土耳其", 2, 0, "FT"),
    ("E", 1, 6, 15,  1,  0, "德国", "库拉索", 7, 1, "FT"),
    ("E", 1, 6, 15,  7,  0, "科特迪瓦", "厄瓜多尔", 1, 0, "FT"),
    ("F", 1, 6, 15,  4,  0, "荷兰", "日本", 2, 2, "FT"),
    ("F", 1, 6, 15, 10,  0, "瑞典", "突尼斯", 5, 1, "FT"),
    ("G", 1, 6, 16,  3,  0, "比利时", "埃及", 1, 1, "FT"),
    ("G", 1, 6, 16,  9,  0, "伊朗", "新西兰", 2, 2, "FT"),
    ("H", 1, 6, 16,  0,  0, "西班牙", "佛得角", 0, 0, "FT"),
    ("H", 1, 6, 16,  6,  0, "沙特阿拉伯", "乌拉圭", 1, 1, "FT"),
    ("I", 1, 6, 17,  3,  0, "法国", "塞内加尔", 3, 1, "FT"),
    ("I", 1, 6, 17,  6,  0, "伊拉克", "挪威", 1, 4, "FT"),
    ("J", 1, 6, 17,  9,  0, "阿根廷", "阿尔及利亚", 3, 0, "FT"),
    ("J", 1, 6, 17, 12,  0, "奥地利", "约旦", 3, 1, "FT"),
    ("K", 1, 6, 18,  1,  0, "葡萄牙", "民主刚果", 1, 1, "FT"),
    ("K", 1, 6, 18, 10,  0, "乌兹别克斯坦", "哥伦比亚", 1, 3, "FT"),
    ("L", 1, 6, 18,  4,  0, "英格兰", "克罗地亚", 4, 2, "FT"),
    ("L", 1, 6, 18,  7,  0, "加纳", "巴拿马", 1, 0, "FT"),
    # === 第2轮 ===
    ("A", 2, 6, 19,  0,  0, "捷克", "南非", 1, 1, "FT"),
    ("A", 2, 6, 19,  9,  0, "墨西哥", "韩国", 1, 0, "FT"),
    ("B", 2, 6, 19,  3,  0, "瑞士", "波黑", 4, 1, "FT"),
    ("B", 2, 6, 19,  6,  0, "加拿大", "卡塔尔", 6, 0, "FT"),
    ("C", 2, 6, 20,  6,  0, "苏格兰", "摩洛哥", None, None, "UP"),
    ("C", 2, 6, 20,  8, 30, "巴西", "海地", None, None, "UP"),
    ("D", 2, 6, 20,  3,  0, "美国", "澳大利亚", None, None, "UP"),
    ("D", 2, 6, 20, 11,  0, "土耳其", "巴拉圭", None, None, "UP"),
    ("E", 2, 6, 21,  4,  0, "德国", "科特迪瓦", None, None, "UP"),
    ("E", 2, 6, 21,  8,  0, "厄瓜多尔", "库拉索", None, None, "UP"),
    ("F", 2, 6, 21,  1,  0, "荷兰", "瑞典", None, None, "UP"),
    ("F", 2, 6, 21, 12,  0, "突尼斯", "日本", None, None, "UP"),
    ("G", 2, 6, 22,  3,  0, "比利时", "伊朗", None, None, "UP"),
    ("G", 2, 6, 22,  9,  0, "新西兰", "埃及", None, None, "UP"),
    ("H", 2, 6, 22,  0,  0, "西班牙", "沙特阿拉伯", None, None, "UP"),
    ("H", 2, 6, 22,  6,  0, "乌拉圭", "佛得角", None, None, "UP"),
    ("I", 2, 6, 23,  5,  0, "法国", "伊拉克", None, None, "UP"),
    ("I", 2, 6, 23,  8,  0, "挪威", "塞内加尔", None, None, "UP"),
    ("J", 2, 6, 23,  1,  0, "阿根廷", "奥地利", None, None, "UP"),
    ("J", 2, 6, 23, 11,  0, "约旦", "阿尔及利亚", None, None, "UP"),
    ("K", 2, 6, 24,  1,  0, "葡萄牙", "乌兹别克斯坦", None, None, "UP"),
    ("K", 2, 6, 24, 10,  0, "哥伦比亚", "民主刚果", None, None, "UP"),
    ("L", 2, 6, 24,  4,  0, "英格兰", "加纳", None, None, "UP"),
    ("L", 2, 6, 24,  7,  0, "巴拿马", "克罗地亚", None, None, "UP"),
    # === 第3轮 ===
    ("A", 3, 6, 25,  9,  0, "捷克", "墨西哥", None, None, "UP"),
    ("A", 3, 6, 25,  9,  0, "南非", "韩国", None, None, "UP"),
    ("B", 3, 6, 25,  3,  0, "瑞士", "加拿大", None, None, "UP"),
    ("B", 3, 6, 25,  3,  0, "波黑", "卡塔尔", None, None, "UP"),
    ("C", 3, 6, 25,  6,  0, "苏格兰", "巴西", None, None, "UP"),
    ("C", 3, 6, 25,  6,  0, "摩洛哥", "海地", None, None, "UP"),
    ("D", 3, 6, 26, 10,  0, "土耳其", "美国", None, None, "UP"),
    ("D", 3, 6, 26, 10,  0, "巴拉圭", "澳大利亚", None, None, "UP"),
    ("E", 3, 6, 26,  4,  0, "厄瓜多尔", "德国", None, None, "UP"),
    ("E", 3, 6, 26,  4,  0, "库拉索", "科特迪瓦", None, None, "UP"),
    ("F", 3, 6, 26,  7,  0, "突尼斯", "荷兰", None, None, "UP"),
    ("F", 3, 6, 26,  7,  0, "日本", "瑞典", None, None, "UP"),
    ("G", 3, 6, 27, 11,  0, "新西兰", "比利时", None, None, "UP"),
    ("G", 3, 6, 27, 11,  0, "埃及", "伊朗", None, None, "UP"),
    ("H", 3, 6, 27,  8,  0, "乌拉圭", "西班牙", None, None, "UP"),
    ("H", 3, 6, 27,  8,  0, "佛得角", "沙特阿拉伯", None, None, "UP"),
    ("I", 3, 6, 27,  3,  0, "挪威", "法国", None, None, "UP"),
    ("I", 3, 6, 27,  3,  0, "塞内加尔", "伊拉克", None, None, "UP"),
    ("J", 3, 6, 28, 10,  0, "约旦", "阿根廷", None, None, "UP"),
    ("J", 3, 6, 28, 10,  0, "阿尔及利亚", "奥地利", None, None, "UP"),
    ("K", 3, 6, 28,  7, 30, "哥伦比亚", "葡萄牙", None, None, "UP"),
    ("K", 3, 6, 28,  7, 30, "民主刚果", "乌兹别克斯坦", None, None, "UP"),
    ("L", 3, 6, 28,  5,  0, "巴拿马", "英格兰", None, None, "UP"),
    ("L", 3, 6, 28,  5,  0, "克罗地亚", "加纳", None, None, "UP"),
]


# ============================================================
# 数据引擎 — 封装积分计算和赛程分组逻辑
# ============================================================
class WorldCupData:
    """纯本地数据引擎，支持从网络（球迷屋）更新比分"""

    CACHE_FILE = "worldcup_cache.json"

    def __init__(self):
        self.standings = {}
        self.all_matches = []
        self.online = False
        self.last_fetch = None
        self._build()

    # ---- 离线默认数据 ----
    def _build(self):
        """用 ALL_MATCHES 构建积分榜和赛程"""
        for g, teams in GROUPS.items():
            self.standings[g] = [
                {"team": t, "w": 0, "d": 0, "l": 0, "gf": 0, "ga": 0, "gd": 0, "pts": 0}
                for t in teams
            ]

        self.all_matches = []
        for (grp, rnd, month, day, hour, minute, home, away, hs, aws, status) in ALL_MATCHES:
            dt = datetime(2026, month, day)
            weekday = WEEKDAY_MAP[dt.weekday()]
            date_str = f"{month:02d}-{day:02d}"
            time_str = f"{hour:02d}:{minute:02d}"

            match_info = {
                "group": grp, "round": rnd,
                "date_key": (month, day),
                "date_str": date_str,
                "time": time_str,
                "home": home, "away": away,
                "home_score": hs, "away_score": aws,
                "status": status,
            }

            # 完赛场更新积分
            if status == "FT" and hs is not None and aws is not None:
                self._update_standings(grp, home, away, hs, aws)

            self.all_matches.append(match_info)

        # 排序
        for group in self.standings:
            for t in self.standings[group]:
                t["gd"] = t["gf"] - t["ga"]
            self.standings[group].sort(
                key=lambda x: (x["pts"], x["gd"], x["gf"]), reverse=True
            )

    def _update_standings(self, grp, home, away, hs, aws):
        """根据比分更新积分榜"""
        for t in self.standings[grp]:
            if t["team"] == home:
                t["gf"] += hs; t["ga"] += aws
                if hs > aws:   t["w"] += 1; t["pts"] += 3
                elif hs == aws: t["d"] += 1; t["pts"] += 1
                else:           t["l"] += 1
            elif t["team"] == away:
                t["gf"] += aws; t["ga"] += hs
                if aws > hs:   t["w"] += 1; t["pts"] += 3
                elif hs == aws: t["d"] += 1; t["pts"] += 1
                else:           t["l"] += 1

    def update_from_network(self):
        """
        联网从球迷屋(qiumiwu.com)拉取最新比分。
        成功返回 True，失败返回 False（静默降级到本地数据）。
        Kivy 端在子线程中调用，主线程刷新 UI。
        """
        try:
            import urllib.request
            import urllib.error
            from lxml import html as lxml_html

            url = "https://www.qiumiwu.com/worldcup"
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36",
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "zh-CN,zh;q=0.9",
            })
            with urllib.request.urlopen(req, timeout=10) as resp:
                raw = resp.read().decode("utf-8", errors="ignore")

            tree = lxml_html.fromstring(raw)
            # 球迷屋 DOM 解析示例（按实际页面结构调整 xpath）
            rows = tree.xpath('//div[contains(@class,"match-list")]/div[@class="item"]')
            updated = 0
            for row in rows:
                try:
                    home_t = row.xpath('.//span[contains(@class,"team-home")]/text()')
                    away_t = row.xpath('.//span[contains(@class,"team-away")]/text()')
                    score_t = row.xpath('.//span[contains(@class,"score")]/text()')
                    status_t = row.xpath('.//span[contains(@class,"status")]/text()')
                    if not home_t or not away_t:
                        continue
                    home = home_t[0].strip()
                    away = away_t[0].strip()
                    status = status_t[0].strip() if status_t else "UP"
                    hs, aws = None, None
                    if score_t and "-" in score_t[0]:
                        parts = score_t[0].split("-")
                        hs = int(parts[0].strip())
                        aws = int(parts[1].strip())
                    # 找到对应比赛更新
                    for m in self.all_matches:
                        if m["home"] == home and m["away"] == away:
                            m["home_score"] = hs
                            m["away_score"] = aws
                            m["status"] = "FT" if status in ("FT", "完赛") else "UP"
                            updated += 1
                except Exception:
                    pass

            if updated > 0:
                # 重建积分榜
                for g in GROUPS:
                    for t in self.standings[g]:
                        t["w"] = t["d"] = t["l"] = t["gf"] = t["ga"] = t["pts"] = 0
                for m in self.all_matches:
                    if m["status"] == "FT" and m["home_score"] is not None:
                        self._update_standings(
                            m["group"], m["home"], m["away"],
                            m["home_score"], m["away_score"]
                        )
                for group in self.standings:
                    for t in self.standings[group]:
                        t["gd"] = t["gf"] - t["ga"]
                    self.standings[group].sort(
                        key=lambda x: (x["pts"], x["gd"], x["gf"]), reverse=True
                    )
                self.last_fetch = datetime.now().strftime("%H:%M")
                self.online = True
                self._save_cache()
                return True
        except Exception:
            pass
        return False

    def _save_cache(self):
        """保存缓存到本地（用于离线展示）"""
        try:
            with open(self.CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump({
                    "standings": self.standings,
                    "matches": self.all_matches,
                    "last_fetch": self.last_fetch,
                }, f, ensure_ascii=False, default=str)
        except Exception:
            pass

    def load_cache(self):
        """从本地缓存加载数据"""
        try:
            with open(self.CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.standings = data.get("standings", {})
            self.all_matches = data.get("matches", [])
            self.last_fetch = data.get("last_fetch")
            self.online = False
            return True
        except Exception:
            return False

    def get_matches_by_date(self):
        """按日期分组返回 [(date_key, date_full, matches_list)]"""
        dates = {}
        for m in self.all_matches:
            dk = m["date_key"]
            if dk not in dates:
                count = sum(
                    1 for x in ALL_MATCHES if x[2] == dk[0] and x[3] == dk[1]
                )
                dt = datetime(2026, dk[0], dk[1])
                weekday = WEEKDAY_MAP[dt.weekday()]
                dates[dk] = (f"{dk[0]:02d}月{dk[1]:02d}日 {weekday}({count}场)", [])
            dates[dk][1].append(m)
        return sorted(dates.items(), key=lambda x: x[0])

    def get_third_place(self):
        """返回各组第三名按积分排序"""
        third = []
        for gn in sorted(self.standings.keys()):
            teams = self.standings[gn]
            if len(teams) >= 3:
                td = dict(teams[2])
                td["group"] = gn
                third.append(td)
        third.sort(key=lambda x: (x["pts"], x["gd"], x["gf"]), reverse=True)
        return third


# ============================================================
# 辅助函数：创建统一风格的 Label / Button
# ============================================================
def lbl(text, size=14, color=C_TEXT, bold=False, halign="left",
        valign="middle", markup=False, shorten=False, shorten_from="right"):
    """快捷创建深色主题 Label"""
    lb = Label(
        text=str(text),
        font_size=f"{size}sp",
        color=gch(color),
        bold=bold,
        halign=halign,
        valign=valign,
        markup=markup,
        shorten=shorten,
        shorten_from=shorten_from,
        size_hint_y=None,
        height="40dp",
        text_size=(None, None),
    )
    return lb


def card_widget(bg=C_CARD, radius=12, padding=10, spacing=6):
    """快捷创建卡片 BoxLayout"""
    w = BoxLayout(
        orientation="vertical",
        size_hint_y=None,
        height="1dp",   # 动态高度由内容撑开
        padding=padding,
        spacing=spacing,
    )
    with w.canvas.before:
        Color(*gch(bg))
        w._rect = Rectangle(pos=w.pos, size=w.size)
    w.bind(pos=lambda *_: setattr(w._rect, 'pos', w.pos))
    w.bind(size=lambda *_: setattr(w._rect, 'size', w.size))
    return w


def row_widget(children_and_widths, bg=C_CARD, height=44,
               line_bottom=True, line_color=C_BORDER):
    """
    children_and_widths: [(widget, width_factor_or_None), ...]
    width_factor=None 表示该 widget 自适应宽度并撑满剩余空间
    """
    row = BoxLayout(
        size_hint_y=None,
        height=f"{height}dp",
        padding=(10, 0, 10, 0),
        spacing=0,
    )
    with row.canvas.before:
        Color(*gch(bg))
        row._rect = Rectangle(pos=row.pos, size=row.size)
    row.bind(pos=lambda *_: setattr(row._rect, 'pos', row.pos))
    row.bind(size=lambda *_: setattr(row._rect, 'size', row.size))

    stretch_count = 0
    fixed_widgets = []
    for w, wf in children_and_widths:
        if wf is None:
            stretch_count += 1
            fixed_widgets.append((w, "1", True))
        elif isinstance(wf, (int, float)):
            fixed_widgets.append((w, str(wf), False))
        else:
            fixed_widgets.append((w, "0", True))

    for w, sz, stretch in fixed_widgets:
        w.size_hint_x = None if not stretch else 1
        if not stretch:
            w.width = f"{int(wf)}dp"
        row.add_widget(w)

    # 底部分隔线
    if line_bottom:
        with row.canvas.after:
            Color(*gch(line_color))
            row._line = Rectangle(
                pos=(row.x, row.y),
                size=(row.width, 1)
            )
        row.bind(pos=lambda *_: setattr(row._line, 'pos', (row.x, row.y)))
        row.bind(size=lambda *_: setattr(row._line, 'size', (row.width, 1)))

    return row


# ============================================================
# Tab 1: 赛程 — 按日期分组
# ============================================================
class ScheduleScreen(Screen):
    def __init__(self, data, **kwargs):
        super().__init__(**kwargs)
        self.data = data
        self.name = "schedule"
        self._build()

    def _build(self):
        root = BoxLayout(orientation="vertical", spacing=0, padding=0)

        # --- 顶部状态栏 ---
        status_bar = BoxLayout(
            size_hint_y=None, height="36dp",
            padding=(12, 0, 12, 0), spacing=8
        )
        with status_bar.canvas.before:
            Color(*gch(C_HEADER_BG))
            Rectangle(pos=status_bar.pos, size=status_bar.size)
        status_bar.bind(pos=lambda *_, w=status_bar: w.canvas.before.clear())

        online_dot = Label(text="[color=#3fb950]●[/color] 在线",
                           markup=True, font_size="11sp",
                           color=gch(C_TEXT_SEC), size_hint_x=None, width="60dp",
                           halign="left", valign="middle")
        online_dot.text_size = (60, None)
        refresh_btn = Button(
            text="刷新",
            font_size="12sp",
            size_hint_x=None, width="56dp",
            background_color=gch(C_BLUE_DARK),
            background_normal="",
            border=(0, 0, 0, 0),
            on_press=lambda *_: self._do_refresh(),
        )
        src_lbl = Label(
            text="数据源: 球迷屋 qiumiwu.com",
            font_size="11sp", color=gch(C_TEXT_SEC),
            halign="right", valign="middle", markup=True,
        )
        src_lbl.text_size = (None, None)
        status_bar.add_widget(online_dot)
        status_bar.add_widget(refresh_btn)
        status_bar.add_widget(src_lbl)

        root.add_widget(status_bar)

        # --- 滚动内容区 ---
        scroll = ScrollView(
            do_scroll_x=False,
            bar_color=gch(C_BORDER),
            bar_inactive_color=gch(C_BORDER),
            scroll_type=["bars"],
        )
        content = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=8,
            padding=(10, 8, 10, 16),
        )
        content.bind(minimum_height=content.setter("height"))

        dates = self.data.get_matches_by_date()
        for date_key, (date_full, matches) in dates:
            card = self._date_card(date_full, matches)
            content.add_widget(card)

        scroll.add_widget(content)
        root.add_widget(scroll)

        self.add_widget(root)

    def _date_card(self, date_full, matches):
        """单个日期卡片: 标题 + 比赛列表"""
        card = card_widget(bg=C_CARD, radius=10, padding=0, spacing=0)

        # 标题栏
        hdr = BoxLayout(size_hint_y=None, height="38dp", padding=(12, 0, 12, 0))
        with hdr.canvas.before:
            Color(*gch(C_DATE_HDR))
            Rectangle(pos=hdr.pos, size=hdr.size)
        hdr_lbl = Label(
            text=date_full,
            font_size="13sp", bold=True,
            color=gch(C_TEXT),
            halign="left", valign="middle",
        )
        hdr_lbl.text_size = (None, None)
        hdr.add_widget(hdr_lbl)
        card.add_widget(hdr)

        # 表头
        card.add_widget(self._table_header())

        # 比赛行
        for m in matches:
            card.add_widget(self._match_row(m))

        return card

    def _table_header(self):
        """表格表头"""
        h = row_widget([], bg=C_HEADER_BG, height=32, line_bottom=True, line_color=C_BORDER)
        cols = [
            (lbl("[color=#8b949e]赛事[/color]", size=10, markup=True, halign="center", valign="middle"), 68),
            (lbl("[color=#8b949e]时间[/color]", size=10, markup=True, halign="center", valign="middle"), 52),
            (lbl("[color=#8b949e]状态[/color]", size=10, markup=True, halign="center", valign="middle"), 48),
            (lbl("[color=#8b949e]主队[/color]", size=10, markup=True, halign="left", valign="middle"), None),
            (lbl("[color=#8b949e]比分[/color]", size=10, markup=True, halign="center", valign="middle"), 58),
            (lbl("[color=#8b949e]客队[/color]", size=10, markup=True, halign="right", valign="middle"), None),
        ]
        inner = BoxLayout(size_hint_y=None, height="32dp", padding=(10, 0, 10, 0), spacing=0)
        for lbl_w, w in cols:
            if w:
                lbl_w.size_hint_x = None
                lbl_w.width = f"{w}dp"
            else:
                lbl_w.size_hint_x = 1
            inner.add_widget(lbl_w)
        h.add_widget(inner)
        return h

    def _match_row(self, m):
        """单场比赛行"""
        is_even = self.data.all_matches.index(m) % 2 == 0
        bg = C_CARD if is_even else C_CARD_ALT
        row = BoxLayout(size_hint_y=None, height="46dp", padding=(10, 0, 10, 0), spacing=0)

        home_flag = FLAGS.get(m["home"], "\U0001f3c0")
        away_flag = FLAGS.get(m["away"], "\U0001f3c0")

        # 赢球队高亮
        if m["status"] == "FT" and m["home_score"] is not None:
            win_color = C_TEAM_WIN
        else:
            win_color = C_TEXT

        # 列1: 赛事
        g1 = lbl(f"{m['group']}组{m['round']}轮",
                 size=10, bold=True, color=C_BLUE,
                 halign="center", valign="middle")
        g1.size_hint_x = None; g1.width = "68dp"

        # 列2: 时间
        g2 = lbl(m["time"], size=11, color=C_TEXT,
                 halign="center", valign="middle")
        g2.size_hint_x = None; g2.width = "52dp"

        # 列3: 状态
        st_map = {"FT": "完场", "UP": "未开"}
        sc_map = {"FT": C_GREEN, "UP": C_TEXT_SEC}
        st_color = sc_map.get(m["status"], C_TEXT_SEC)
        g3 = lbl(st_map.get(m["status"], m["status"]),
                 size=10, bold=True, color=st_color,
                 halign="center", valign="middle")
        g3.size_hint_x = None; g3.width = "48dp"

        # 列4: 主队
        home_color = C_TEAM_WIN if (m["status"] == "FT" and m["home_score"] is not None
                                    and m["home_score"] > m["away_score"]) else C_TEXT
        g4 = lbl(f"{home_flag} {m['home']}",
                 size=12, color=home_color,
                 halign="left", valign="middle", shorten=True, shorten_from="right")
        g4.size_hint_x = 1

        # 列5: 比分
        if m["status"] == "FT" and m["home_score"] is not None:
            score_txt = f"{m['home_score']}-{m['away_score']}"
            g5 = lbl(score_txt, size=14, bold=True, color=C_TEXT,
                     halign="center", valign="middle")
        else:
            g5 = lbl("VS", size=12, bold=True, color=C_ORANGE,
                     halign="center", valign="middle")
        g5.size_hint_x = None; g5.width = "58dp"

        # 列6: 客队
        away_color = C_TEAM_WIN if (m["status"] == "FT" and m["away_score"] is not None
                                     and m["away_score"] > m["home_score"]) else C_TEXT
        g6 = lbl(f"{m['away']} {away_flag}",
                 size=12, color=away_color,
                 halign="right", valign="middle", shorten=True, shorten_from="left")
        g6.size_hint_x = 1

        row.add_widget(g1)
        row.add_widget(g2)
        row.add_widget(g3)
        row.add_widget(g4)
        row.add_widget(g5)
        row.add_widget(g6)

        # 底部分隔线
        with row.canvas.after:
            Color(*gch(C_BORDER))
            Rectangle(pos=(row.x + 10, row.y), size=(row.width - 20, 1))
        row.bind(
            pos=lambda *_: Rectangle(
                pos=(row.x + 10, row.y), size=(row.width - 20, 1)
            ).__setattr__("pos", (row.x + 10, row.y))
        )

        return row

    def _do_refresh(self):
        """子线程联网刷新，完成后切回主线程更新 UI"""
        def fetch():
            ok = self.data.update_from_network()
            Clock.schedule_once(lambda dt: self._on_refresh_done(ok), -1)

        threading.Thread(target=fetch, daemon=True).start()

    def _on_refresh_done(self, ok):
        self._build()
        # 通知其他 Tab 刷新
        sm = self.manager
        if sm:
            for name in ("standings", "third"):
                s = sm.get_screen(name)
                if hasattr(s, "_build"):
                    s._build()


# ============================================================
# Tab 2: 积分榜 — 12组 3列网格
# ============================================================
class StandingsScreen(Screen):
    def __init__(self, data, **kwargs):
        super().__init__(**kwargs)
        self.data = data
        self.name = "standings"
        self._build()

    def _build(self):
        root = BoxLayout(orientation="vertical", spacing=0, padding=0)

        # 顶部说明
        top_bar = BoxLayout(
            size_hint_y=None, height="34dp",
            padding=(12, 0, 12, 0),
        )
        with top_bar.canvas.before:
            Color(*gch(C_HEADER_BG))
            Rectangle(pos=top_bar.pos, size=top_bar.size)
        top_bar.add_widget(lbl(
            "[color=#58a6ff]🟢前二晋级[/color]  [color=#d29922]🔵前三[/color]  12组小组积分",
            size="11sp", markup=True, halign="left", valign="middle"
        ))
        root.add_widget(top_bar)

        scroll = ScrollView(
            do_scroll_x=False,
            bar_color=gch(C_BORDER),
            bar_inactive_color=gch(C_BORDER),
            scroll_type=["bars"],
        )
        grid = GridLayout(
            cols=1,
            size_hint_y=None,
            spacing=8,
            padding=(8, 8, 8, 16),
        )
        grid.bind(minimum_height=grid.setter("height"))

        for gn in sorted(self.data.standings.keys()):
            card = self._group_card(gn, self.data.standings[gn])
            grid.add_widget(card)

        scroll.add_widget(grid)
        root.add_widget(scroll)
        self.clear_widgets()
        self.add_widget(root)

    def _group_card(self, gname, teams):
        """单个小组积分卡片"""
        card = card_widget(bg=C_CARD, radius=10, padding=0, spacing=0)

        # 组标题
        hdr = BoxLayout(size_hint_y=None, height="38dp", padding=(12, 0, 12, 0))
        with hdr.canvas.before:
            Color(*gch(C_DATE_HDR))
            Rectangle(pos=hdr.pos, size=hdr.size)
        hdr_lbl = Label(
            text=f"[color=#58a6ff]{gname}[/color] 组 小组积分",
            font_size="13sp", bold=True,
            markup=True, halign="left", valign="middle",
        )
        hdr_lbl.text_size = (None, None)
        hdr.add_widget(hdr_lbl)
        card.add_widget(hdr)

        # 表头
        card.add_widget(self._header_row())

        # 球队行
        for idx, t in enumerate(teams):
            card.add_widget(self._team_row(t, idx))

        return card

    def _header_row(self):
        h = BoxLayout(size_hint_y=None, height="30dp", padding=(8, 0, 8, 0))
        with h.canvas.before:
            Color(*gch(C_HEADER_BG))
            Rectangle(pos=h.pos, size=h.size)
        cols = [
            ("#", 28, "center"),
            ("球队", None, "left"),
            ("胜", 28, "center"),
            ("平", 28, "center"),
            ("负", 28, "center"),
            ("净胜", 36, "center"),
            ("积分", 36, "center"),
        ]
        for txt, w, align in cols:
            lb = Label(
                text=f"[color=#8b949e]{txt}[/color]",
                font_size="10sp", markup=True,
                halign=align, valign="middle",
                size_hint_x=None if w else 1,
                width=f"{w}dp" if w else None,
            )
            lb.text_size = (None, None)
            h.add_widget(lb)
        return h

    def _team_row(self, t, idx):
        row = BoxLayout(size_hint_y=None, height="40dp", padding=(8, 0, 8, 0))

        # 行背景色：前二绿，前四橙
        if idx == 0:
            bg = C_GREEN_LIGHT
        elif idx == 1:
            bg = C_ORANGE_LIGHT
        else:
            bg = C_CARD if idx % 2 == 0 else C_CARD_ALT

        with row.canvas.before:
            Color(*gch(bg))
            Rectangle(pos=row.pos, size=row.size)

        rank_color = C_GREEN if idx == 0 else (C_ORANGE if idx == 1 else C_TEXT_SEC)
        gd = t["gd"]
        gd_str = f"+{gd}" if gd > 0 else str(gd)
        gd_color = C_GREEN if gd > 0 else (C_RED if gd < 0 else C_TEXT_SEC)

        flag = FLAGS.get(t["team"], "\U0001f3c0")

        # #排
        r1 = Label(
            text=str(idx + 1), font_size="12sp", bold=True,
            color=gch(rank_color), halign="center", valign="middle",
            size_hint_x=None, width="28dp",
        )

        # 球队
        r2 = Label(
            text=f"{flag}  {t['team']}",
            font_size="12sp", color=gch(C_TEXT),
            halign="left", valign="middle",
            size_hint_x=1,
            shorten=True, shorten_from="right",
        )
        r2.text_size = (None, None)

        # 胜
        r3 = Label(
            text=str(t["w"]), font_size="11sp", color=gch(C_TEXT),
            halign="center", valign="middle",
            size_hint_x=None, width="28dp",
        )

        # 平
        r4 = Label(
            text=str(t["d"]), font_size="11sp", color=gch(C_TEXT),
            halign="center", valign="middle",
            size_hint_x=None, width="28dp",
        )

        # 负
        r5 = Label(
            text=str(t["l"]), font_size="11sp", color=gch(C_TEXT),
            halign="center", valign="middle",
            size_hint_x=None, width="28dp",
        )

        # 净胜
        r6 = Label(
            text=gd_str, font_size="11sp", bold=True,
            color=gch(gd_color), halign="center", valign="middle",
            size_hint_x=None, width="36dp",
        )

        # 积分
        r7 = Label(
            text=str(t["pts"]), font_size="13sp", bold=True,
            color=gch(C_BLUE), halign="center", valign="middle",
            size_hint_x=None, width="36dp",
        )

        row.add_widget(r1)
        row.add_widget(r2)
        row.add_widget(r3)
        row.add_widget(r4)
        row.add_widget(r5)
        row.add_widget(r6)
        row.add_widget(r7)

        # 底部分隔
        with row.canvas.after:
            Color(*gch(C_BORDER))
            Rectangle(pos=(row.x + 8, row.y), size=(row.width - 16, 1))

        return row


# ============================================================
# Tab 3: 第三名排名
# ============================================================
class ThirdPlaceScreen(Screen):
    def __init__(self, data, **kwargs):
        super().__init__(**kwargs)
        self.data = data
        self.name = "third"
        self._build()

    def _build(self):
        root = BoxLayout(orientation="vertical", spacing=0, padding=0)

        # 标题
        hdr = BoxLayout(
            size_hint_y=None, height="46dp",
            padding=(14, 0, 14, 0),
        )
        with hdr.canvas.before:
            Color(*gch(C_HEADER_BG))
            Rectangle(pos=hdr.pos, size=hdr.size)
        hdr.add_widget(lbl(
            "[color=#58a6ff]\U0001f949[/color] 各组第三名 · 前8名晋级淘汰赛",
            size="15sp", bold=True, markup=True,
            halign="left", valign="middle",
        ))
        root.add_widget(hdr)

        scroll = ScrollView(
            do_scroll_x=False,
            bar_color=gch(C_BORDER),
            bar_inactive_color=gch(C_BORDER),
            scroll_type=["bars"],
        )
        content = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=6,
            padding=(10, 8, 10, 16),
        )
        content.bind(minimum_height=content.setter("height"))

        third = self.data.get_third_place()

        # 表格头
        content.add_widget(self._header_row())

        # 第三名行
        for idx, t in enumerate(third):
            top8 = idx < 8
            bg = C_GREEN_LIGHT if top8 else C_CARD_ALT
            content.add_widget(self._third_row(t, idx, top8, bg))

        # 说明
        note = lbl(
            "[color=#3fb950]🟢 前8名晋级[/color]  [color=#f85149]🔴 后4名淘汰[/color]\n"
            "积分相同比较: 净胜球 → 进球数 → 胜负关系",
            size="11sp", markup=True, halign="center", valign="middle",
        )
        note.size_hint_y = None
        note.height = "52dp"
        content.add_widget(note)

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.clear_widgets()
        self.add_widget(root)

    def _header_row(self):
        h = BoxLayout(size_hint_y=None, height="32dp", padding=(8, 0, 8, 0))
        with h.canvas.before:
            Color(*gch(C_HEADER_BG))
            Rectangle(pos=h.pos, size=h.size)
        cols = [
            ("#", 30),
            ("球队", None),
            ("组", 30),
            ("胜", 26),
            ("平", 26),
            ("负", 26),
            ("进球", 32),
            ("失球", 32),
            ("净胜", 36),
            ("积分", 36),
        ]
        for txt, w in cols:
            lb = Label(
                text=f"[color=#8b949e]{txt}[/color]",
                font_size="10sp", markup=True,
                halign="center", valign="middle",
                size_hint_x=None if w else 1,
                width=f"{w}dp" if w else None,
            )
            lb.text_size = (None, None)
            h.add_widget(lb)
        return h

    def _third_row(self, t, idx, top8, bg):
        row = BoxLayout(size_hint_y=None, height="42dp", padding=(8, 0, 8, 0))
        with row.canvas.before:
            Color(*gch(bg))
            Rectangle(pos=row.pos, size=row.size)

        flag = FLAGS.get(t["team"], "\U0001f3c0")
        gd = t["gd"]
        gd_str = f"+{gd}" if gd > 0 else str(gd)
        gd_color = C_GREEN if gd > 0 else (C_RED if gd < 0 else C_TEXT_SEC)
        rank_color = C_GREEN if top8 else C_RED
        pts_color = C_BLUE

        data = [
            (str(idx + 1), rank_color, 30, "center"),
            (f"{flag}  {t['team']}", C_TEXT, None, "left"),
            (t["group"], C_BLUE, 30, "center"),
            (str(t["w"]), C_TEXT, 26, "center"),
            (str(t["d"]), C_TEXT, 26, "center"),
            (str(t["l"]), C_TEXT, 26, "center"),
            (str(t["gf"]), C_TEXT, 32, "center"),
            (str(t["ga"]), C_TEXT, 32, "center"),
            (gd_str, gd_color, 36, "center"),
            (str(t["pts"]), pts_color, 36, "center"),
        ]

        for txt, color, w, align in data:
            is_rank = (txt == str(idx + 1))
            lb = Label(
                text=txt,
                font_size="11sp",
                bold=is_rank,
                color=gch(color),
                halign=align, valign="middle",
                size_hint_x=None if w else 1,
                width=f"{w}dp" if w else None,
                shorten=True, shorten_from="right" if align == "left" else "left",
            )
            lb.text_size = (None, None)
            row.add_widget(lb)

        # 底部分隔
        with row.canvas.after:
            Color(*gch(C_BORDER))
            Rectangle(pos=(row.x + 8, row.y), size=(row.width - 16, 1))

        return row


# ============================================================
# 主 App — 统一管理 ScreenManager + Tab 导航
# ============================================================
class WorldCupApp(App):
    title = "⚽ 2026世界杯追踪器"
    data = None
    sm = None

    def build(self):
        # 全局深色背景
        Window.clearcolor = gch(C_BG)

        self.data = WorldCupData()
        # 尝试加载本地缓存
        self.data.load_cache()

        # ScreenManager
        self.sm = ScreenManager()
        self.sm.add_widget(ScheduleScreen(self.data))
        self.sm.add_widget(StandingsScreen(self.data))
        self.sm.add_widget(ThirdPlaceScreen(self.data))

        # Tab 导航栏（底部）
        root = BoxLayout(orientation="vertical")
        root.add_widget(self.sm)

        # 底部 Tab 栏
        nav = BoxLayout(
            size_hint_y=None, height="50dp",
            padding=(8, 4, 8, 4),
            spacing=4,
        )
        with nav.canvas.before:
            Color(*gch(C_HEADER_BG))
            Rectangle(pos=nav.pos, size=nav.size)

        tabs = [
            ("\U0001f4c5 赛程", "schedule"),
            ("\U0001f3c6 积分", "standings"),
            ("\U0001f949 第三名", "third"),
        ]
        for i, (title, screen_name) in enumerate(tabs):
            btn = Button(
                text=title,
                font_size="13sp",
                bold=False,
                background_color=gch(C_BLUE_DARK) if i == 0 else gch("transparent"),
                background_normal="",
                border=(0, 0, 0, 0),
                on_press=lambda _, sn=screen_name: self._switch_to(sn),
            )
            nav.add_widget(btn)

        root.add_widget(nav)

        # 启动时尝试联网刷新（后台）
        Clock.schedule_once(lambda dt: self._background_fetch(), 1.5)

        return root

    def _switch_to(self, screen_name):
        self.sm.current = screen_name
        # 更新 Tab 高亮
        nav = self.children[0]
        for i, child in enumerate(nav.children):
            if hasattr(child, "text"):
                is_active = self.sm.current == ["schedule", "standings", "third"][::-1][i]
                child.background_color = gch(C_BLUE_DARK) if is_active else (1, 1, 1, 0)

    def _background_fetch(self):
        def fetch():
            ok = self.data.update_from_network()
            if ok:
                Clock.schedule_once(lambda dt: self._refresh_all(), -1)

        threading.Thread(target=fetch, daemon=True).start()

    def _refresh_all(self):
        for name in ("schedule", "standings", "third"):
            s = self.sm.get_screen(name)
            if hasattr(s, "_build"):
                s._build()


# ============================================================
# 入口
# ============================================================
if __name__ in ("__main__", "__android__", "__main__"):
    WorldCupApp().run()
