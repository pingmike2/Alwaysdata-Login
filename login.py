#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import requests
from bs4 import BeautifulSoup


def alwaysdata_login_api(username, password):
    session = requests.Session()

    headers = {
        "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/137.0.0.0 Safari/537.36",

        "Accept":
            "text/html,application/xhtml+xml,application/xml;q=0.9,"
            "image/avif,image/webp,*/*;q=0.8",

        "Accept-Language":
            "en-US,en;q=0.9",

        "Referer":
            "https://admin.alwaysdata.com/login/",

        "Origin":
            "https://admin.alwaysdata.com"
    }

    session.headers.update(headers)

    login_url = "https://admin.alwaysdata.com/login/"

    try:
        print("🔄 获取登录页...")

        response = session.get(
            login_url,
            timeout=30,
            allow_redirects=True
        )

        print(f"GET Status: {response.status_code}")
        print(f"GET URL: {response.url}")

        if response.status_code != 200:
            print("❌ 登录页访问失败")
            return False

        # 调试前1000字符
        print("\n========== 页面前1000字符 ==========")
        print(response.text[:1000])
        print("===================================\n")

        # 检查常见风控
        page_lower = response.text.lower()

        if (
            "cloudflare" in page_lower
            or "checking your browser" in page_lower
            or "attention required" in page_lower
            or "captcha" in page_lower
        ):
            print("❌ 检测到风控页面")
            return False

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        csrf_input = soup.find(
            "input",
            {"name": "csrfmiddlewaretoken"}
        )

        if not csrf_input:
            print("❌ 未找到 csrfmiddlewaretoken")
            return False

        csrf_token = csrf_input.get("value")

        print(
            f"🔑 CSRF Token: {csrf_token[:20]}..."
        )

        payload = {
            "csrfmiddlewaretoken": csrf_token,
            "login": username,
            "password": password,
            "alive": "on"
        }

        print("🚀 提交登录请求...")

        login_response = session.post(
            login_url,
            data=payload,
            timeout=30,
            allow_redirects=True
        )

        print(f"POST Status: {login_response.status_code}")
        print(f"POST URL: {login_response.url}")

        cookies = session.cookies.get_dict()

        print("\n========== Cookies ==========")
        for k, v in cookies.items():
            print(f"{k} = {v}")
        print("=============================\n")

        print("\n========== 登录后页面前1000字符 ==========")
        print(login_response.text[:1000])
        print("========================================\n")

        # 检查后台首页
        print("🔍 验证登录状态...")

        dashboard = session.get(
            "https://admin.alwaysdata.com/",
            timeout=30
        )

        dashboard_text = dashboard.text.lower()

        success_keywords = [
            "logout",
            "dashboard",
            "accounts",
            "hosting",
            "domains"
        ]

        login_success = any(
            kw in dashboard_text
            for kw in success_keywords
        )

        if login_success:
            print("✅ 登录成功")
            return True

        if "sessionid" in cookies:
            print("⚠️ 已获得 sessionid，但无法确认是否真正登录成功")
            print("Dashboard URL:", dashboard.url)
            return True

        print("❌ 登录失败")
        return False

    except requests.exceptions.Timeout:
        print("❌ 请求超时")
        return False

    except requests.exceptions.ConnectionError:
        print("❌ 网络连接失败")
        return False

    except Exception as e:
        print(f"❌ 未知异常: {e}")
        return False


def main():
    username = os.getenv("ALWAYSDATA_USER")
    password = os.getenv("ALWAYSDATA_PASS")

    if not username:
        print("❌ 缺少环境变量 ALWAYSDATA_USER")
        sys.exit(1)

    if not password:
        print("❌ 缺少环境变量 ALWAYSDATA_PASS")
        sys.exit(1)

    success = alwaysdata_login_api(
        username,
        password
    )

    if success:
        print("🎉 任务完成")
        sys.exit(0)
    else:
        print("💥 任务失败")
        sys.exit(1)


if __name__ == "__main__":
    main()