#!/usr/bin/env python3
"""
骆马湖 WET 模型参数率定工具
================================
用于率定 GETM-FABM-WET 模型的生态参数

使用方式:
    python calibrate.py --param <参数名> --min <最小值> --max <最大值> --obs <观测文件>

Author: GETM-FABM-WET Team
"""

import os
import sys
import numpy as np
import subprocess
from pathlib import Path
import argparse

# 项目路径
PROJECT_DIR = Path(__file__).resolve().parent
CASE_DIR = PROJECT_DIR / "luomahu_case"
BIN_DIR = PROJECT_DIR / "bin"


def run_model():
    """运行模型一次"""
    os.chdir(CASE_DIR)
    result = subprocess.run(
        [BIN_DIR / "getm_cartesian"],
        capture_output=True,
        text=True
    )
    return result.returncode == 0


def read_output(var_name, time_idx=-1, i=None, j=None):
    """
    从输出 NetCDF 读取变量值

    Args:
        var_name: 变量名 (如 'cyanobacteria_concentration')
        time_idx: 时间索引 (-1 表示最后一个)
        i, j: 网格索引 (None 表示平均)
    """
    try:
        from netCDF4 import Dataset

        nc_path = CASE_DIR / "output.nc"
        if not nc_path.exists():
            nc_path = CASE_DIR / "LUOMAHU_WET.3d.nc"

        ds = Dataset(nc_path)

        # 查找变量
        var = None
        for v in ds.variables:
            if var_name.lower() in v.lower():
                var = ds.variables[v]
                break

        if var is None:
            return None

        if i is not None and j is not None:
            return var[time_idx, :, j, i].mean()
        else:
            return var[time_idx, :, :, :].mean()

    except Exception as e:
        print(f"读取输出失败: {e}")
        return None


def objective_function(params, target_var, obs_value):
    """
    目标函数：计算模拟值与观测值的差异

    Args:
        params: 参数字典
        target_var: 目标变量名
        obs_value: 观测值

    Returns:
        差异 (MSE)
    """
    # 这里应该修改 fabm.yaml 中的参数
    # 然后运行模型
    # 最后计算差异

    sim_value = read_output(target_var)
    if sim_value is None:
        return 1e10

    mse = (sim_value - obs_value) ** 2
    return mse


def main():
    parser = argparse.ArgumentParser(
        description="骆马湖 WET 模型参数率定工具"
    )
    parser.add_argument(
        "--param", type=str, required=True,
        help="要率定的参数名"
    )
    parser.add_argument(
        "--min", type=float, default=0.0,
        help="参数最小值"
    )
    parser.add_argument(
        "--max", type=float, default=1.0,
        help="参数最大值"
    )
    parser.add_argument(
        "--obs", type=str,
        help="观测数据文件路径"
    )
    parser.add_argument(
        "--obs-value", type=float,
        help="观测值（如果只有一个值）"
    )
    parser.add_argument(
        "--target", type=str, default="chla",
        help="目标变量名"
    )
    parser.add_argument(
        "--method", type=str, default="grid",
        choices=["grid", "pso", "mcmc"],
        help="率定方法"
    )
    parser.add_argument(
        "--n-iter", type=int, default=50,
        help="迭代次数"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("  骆马湖 WET 模型参数率定")
    print("=" * 60)
    print(f"  参数: {args.param}")
    print(f"  范围: {args.min} ~ {args.max}")
    print(f"  目标变量: {args.target}")
    print(f"  方法: {args.method}")
    print()

    if args.method == "grid":
        print("使用网格搜索法进行率定...")
        best_param = None
        best_mse = 1e10

        n_steps = int(np.sqrt(args.n_iter))
        for p in np.linspace(args.min, args.max, n_steps):
            mse = objective_function({args.param: p}, args.target, args.obs_value)
            if mse < best_mse:
                best_mse = mse
                best_param = p
            print(f"  {args.param}={p:.4f}, MSE={mse:.6f}")

        print()
        print(f"最佳参数: {args.param} = {best_param:.6f}")
        print(f"最小MSE: {best_mse:.6f}")

    else:
        print(f"方法 {args.method} 暂未实现")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
