#!/usr/bin/env python3
"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: run_tests.py
@DateTime: 2025/08/26 15:30:00
@Docs: 测试运行脚本
"""

import os
import subprocess
import sys
from pathlib import Path


def main():
    """运行测试的主函数"""
    # 确保在项目根目录
    project_root = Path(__file__).parent
    os.chdir(project_root)

    # 设置测试环境变量
    os.environ["ENVIRONMENT"] = "testing"
    os.environ["DATABASE_URL"] = "sqlite://:memory:"
    os.environ["REDIS_URL"] = "redis://localhost:6379/15"

    # 基本测试命令
    base_cmd = [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short", "--strict-markers"]

    # 解析命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == "coverage":
            # 运行带覆盖率的测试
            cmd = base_cmd + [
                "--cov=app",
                "--cov-report=term-missing",
                "--cov-report=html:htmlcov",
                "--cov-report=xml:coverage.xml",
            ]
        elif sys.argv[1] == "fast":
            # 快速测试（跳过慢测试）
            cmd = base_cmd + ["-m", "not slow"]
        elif sys.argv[1] == "integration":
            # 仅运行集成测试
            cmd = base_cmd + ["-m", "integration"]
        elif sys.argv[1] == "unit":
            # 仅运行单元测试
            cmd = base_cmd + ["-m", "unit"]
        elif sys.argv[1] == "parallel":
            # 并行运行测试
            cmd = base_cmd + ["-n", "auto"]
        else:
            # 运行特定测试文件或模式
            cmd = base_cmd + [sys.argv[1]]
    else:
        # 默认运行所有测试
        cmd = base_cmd

    print(f"运行命令: {' '.join(cmd)}")
    print("-" * 60)

    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except KeyboardInterrupt:
        print("\n测试被用户中断")
        return 1
    except Exception as e:
        print(f"运行测试时发生错误: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
