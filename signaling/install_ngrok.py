#!/usr/bin/env python3
"""
自动下载和配置ngrok
"""
import os
import sys
import platform
import urllib.request
import zipfile
import tarfile
from pathlib import Path
import subprocess

def get_ngrok_url():
    """获取ngrok下载链接"""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    # 根据系统和架构选择
    if system == "windows":
        if "amd64" in machine or "x86_64" in machine:
            return "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-3.15.10-windows-amd64.zip"
        else:
            return "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-3.15.10-windows-386.zip"
    elif system == "darwin":
        return "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-3.15.10-darwin-arm64.zip"
    elif system == "linux":
        if "aarch64" in machine or "arm64" in machine:
            return "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-3.15.10-linux-arm64.tar.gz"
        else:
            return "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-3.15.10-linux-amd64.tar.gz"
    else:
        raise Exception(f"不支持的系统: {system}")

def download_ngrok(url, dest_dir):
    """下载ngrok"""
    print(f"📥 正在下载ngrok...")
    print(f"📍 下载地址: {url}")
    
    filename = url.split("/")[-1]
    filepath = Path(dest_dir) / filename
    
    try:
        urllib.request.urlretrieve(url, filepath)
        print(f"✅ 下载完成: {filepath}")
        return filepath
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        return None

def extract_ngrok(zip_path, dest_dir):
    """解压ngrok"""
    print(f"📦 正在解压ngrok...")
    
    if zip_path.suffix == ".zip":
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(dest_dir)
    elif zip_path.suffix in ['.tar.gz', '.tgz']:
        with tarfile.open(zip_path, 'r:gz') as tar:
            tar.extractall(dest_dir)
    
    print(f"✅ 解压完成: {dest_dir}")
    
    # 找到ngrok可执行文件
    ngrok_exe = None
    for root, dirs, files in os.walk(dest_dir):
        for f in files:
            if f == "ngrok.exe" or f == "ngrok":
                ngrok_exe = Path(root) / f
                break
        if ngrok_exe:
            break
    
    return ngrok_exe

def configure_ngrok(ngrok_path, token):
    """配置ngrok"""
    print(f"⚙️  正在配置ngrok...")
    
    try:
        # 设置ngrok路径
        result = subprocess.run(
            [str(ngrok_path), "config", "add-authtoken", token],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ ngrok配置完成")
            return True
        else:
            print(f"❌ 配置失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 配置错误: {e}")
        return False

def main():
    """主函数"""
    print()
    print("=" * 50)
    print("  ngrok 自动安装配置工具")
    print("=" * 50)
    print()
    
    # 检查是否已安装
    system = platform.system().lower()
    install_dir = Path.home() / ".ngrok"
    
    if system == "windows":
        ngrok_exe = install_dir / "ngrok.exe"
    else:
        ngrok_exe = install_dir / "ngrok"
    
    if ngrok_exe.exists():
        print(f"✅ ngrok已安装: {ngrok_exe}")
        
        # 检查token配置
        config_file = install_dir / "ngrok.yml"
        if config_file.exists():
            content = config_file.read_text()
            if "authtoken" in content and "2x" in content:
                print(f"✅ ngrok已配置token")
                print()
                print("💡 运行以下命令启动隧道:")
                print(f"   cd E:\\aiprojects\\RemoteDesktop\\signaling")
                print("   uv run python main_ngrok.py")
                print()
                return 0
            else:
                print(f"⚠️  ngrok未配置token")
        else:
            print(f"⚠️  ngrok配置文件不存在")
    else:
        print(f"📥 首次使用，需要下载ngrok")
    
    # 获取token
    token = os.getenv("NGROK_AUTH_TOKEN", "")
    if not token:
        print()
        print("📋 步骤1: 注册ngrok账号")
        print("   访问: https://dashboard.ngrok.com/signup")
        print()
        print("   登录后获取Auth Token:")
        print("   Dashboard -> Getting Started -> Authtoken")
        print()
        print("💡 你可以:")
        print("   1. 设置环境变量后重新运行此脚本")
        print("   2. 手动配置: set NGROK_AUTH_TOKEN=YOUR_TOKEN")
        print()
        return 1
    
    # 下载ngrok
    url = get_ngrok_url()
    zip_path = download_ngrok(url, install_dir)
    
    if not zip_path:
        return 1
    
    # 解压
    ngrok_exe = extract_ngrok(zip_path, install_dir)
    
    if not ngrok_exe:
        print(f"❌ 找不到ngrok可执行文件")
        return 1
    
    # 配置
    if configure_ngrok(ngrok_exe, token):
        print()
        print("=" * 50)
        print("  ✅ ngrok安装配置完成!")
        print("=" * 50)
        print()
        print("📍 ngrok位置:")
        print(f"   {ngrok_exe}")
        print()
        print("💡 下一步:")
        print("   1. 设置环境变量: set NGROK_AUTH_TOKEN=YOUR_TOKEN")
        print("   2. 启动隧道: uv run python main_ngrok.py")
        print()
        
        # 显示ngrok版本
        try:
            result = subprocess.run([str(ngrok_exe), "--version"], capture_output=True, text=True)
            print(f"📦 ngrok版本: {result.stdout.strip()}")
        except:
            pass
        
        print("=" * 50)
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())
