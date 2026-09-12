#!/usr/bin/env python3
"""远程桌面项目 - 依赖安装脚本"""
import subprocess, sys, os, shutil

def run_cmd(cmd, cwd=None):
    print(f"$ {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ 失败: {result.stderr[-500:]}")
        return False
    print(f"✓ 成功")
    return True

def main():
    print("=" * 50)
    print("远程桌面控制软件 - 依赖安装")
    print("=" * 50)
    
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    print("\n[1/2] 安装信令服务器依赖...")
    signaling_dir = os.path.join(project_root, "signaling")
    if os.path.exists(signaling_dir):
        run_cmd("uv sync", cwd=signaling_dir)
    
    print("\n[2/2] Windows端依赖")
    pyhost_dir = os.path.join(project_root, "pyhost")
    if os.path.exists(pyhost_dir):
        venv_dir = os.path.join(pyhost_dir, ".venv")
        if os.path.exists(venv_dir):
            print(f"✓ Windows端虚拟环境已存在: {venv_dir}")
            print(f"  使用方式: cd pyhost && uv run python main.py --token YOUR_TOKEN")
        else:
            print("⚠ Windows端虚拟环境未创建")
            run_cmd("uv sync", cwd=pyhost_dir)
    
    print("\n[3/3] Flutter依赖安装")
    flutter_dir = os.path.join(project_root, "flutter_remote")
    if os.path.exists(flutter_dir):
        if shutil.which("flutter"):
            print("检测到Flutter，运行: flutter pub get")
            run_cmd("flutter pub get", cwd=flutter_dir)
        else:
            print("⚠ 未检测到Flutter")
            print(f"  请手动运行: cd {flutter_dir} && flutter pub get")
    
    print("\n" + "=" * 50)
    print("✓ 依赖安装完成！")
    print("=" * 50)
    print("\n下一步：")
    print("1. 启动信令服务器: cd signaling && uv run python main.py")
    print("2. 启动Windows端: cd pyhost && uv run python main.py --token ABCD12")
    print("3. Android端输入Token连接")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
