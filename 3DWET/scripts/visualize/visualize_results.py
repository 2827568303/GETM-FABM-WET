#!/usr/bin/env python3
"""
可视化脚本：生成GETM-FABM-WET耦合模型结果图
"""
import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset
import os

def plot_3d_results():
    """绘制test_case的3D结果"""
    
    # 读取数据
    nc = Dataset('GETM_FABM_WET_TEST.3d.nc', 'r')
    
    # 获取维度
    time_var = nc.variables['time']
    sigma = nc.variables['sigma']
    xc = nc.variables['xc'][:]
    yc = nc.variables['yc'][:]
    
    # 获取变量
    temp = nc.variables['temp'][0, :, :, :]
    nh4 = nc.variables['abiotic_water_sNH4W'][0, :, :, :]
    no3 = nc.variables['abiotic_water_sNO3W'][0, :, :, :]
    o2 = nc.variables['abiotic_water_sO2W'][0, :, :, :]
    
    # 创建图形
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('GETM-FABM-WET 三维湖泊生态系统模型 - 测试结果', fontsize=14)
    
    # 1. 温度剖面
    ax1 = axes[0, 0]
    mid_j = temp.shape[1] // 2
    im1 = ax1.contourf(xc, sigma, temp[:, mid_j, :].T, cmap='RdYlBu_r')
    ax1.set_xlabel('X (m)')
    ax1.set_ylabel('Sigma Layer')
    ax1.set_title('温度 (°C) - Y中心剖面')
    plt.colorbar(im1, ax=ax1)
    
    # 2. 氨氮剖面
    ax2 = axes[0, 1]
    im2 = ax2.contourf(xc, sigma, nh4[:, mid_j, :].T, cmap='YlOrRd')
    ax2.set_xlabel('X (m)')
    ax2.set_ylabel('Sigma Layer')
    ax2.set_title('氨氮 (gN/m³)')
    plt.colorbar(im2, ax=ax2)
    
    # 3. 溶解氧剖面
    ax3 = axes[1, 0]
    im3 = ax3.contourf(xc, sigma, o2[:, mid_j, :].T, cmap='Blues')
    ax3.set_xlabel('X (m)')
    ax3.set_ylabel('Sigma Layer')
    ax3.set_title('溶解氧 (gO₂/m³)')
    plt.colorbar(im3, ax=ax3)
    
    # 4. 硝氮剖面
    ax4 = axes[1, 1]
    im4 = ax4.contourf(xc, sigma, no3[:, mid_j, :].T, cmap='Greens')
    ax4.set_xlabel('X (m)')
    ax4.set_ylabel('Sigma Layer')
    ax4.set_title('硝氮 (gN/m³)')
    plt.colorbar(im4, ax=ax4)
    
    plt.tight_layout()
    plt.savefig('figure_01_3d_water_quality.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    print("图1: 3D水质结果已保存")
    
    # 图2: 垂直剖面时间序列
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('GETM-FABM-WET 垂直剖面 - 中心网格', fontsize=14)
    
    mid_i = temp.shape[2] // 2
    mid_j = temp.shape[1] // 2
    
    # 绘制各层变化
    layers_to_plot = [0, 2, 5, 9]  # 表层、中层、近底层、底层
    colors = ['red', 'orange', 'blue', 'purple']
    
    # 温度垂直分布
    ax1 = axes[0, 0]
    for k, c in zip(layers_to_plot, colors):
        ax1.plot(temp[k, mid_j, :], xc, '-o', color=c, label=f'Layer {k}', markersize=3)
    ax1.set_xlabel('温度 (°C)')
    ax1.set_ylabel('X (m)')
    ax1.set_title('温度垂直分布')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 氨氮垂直分布
    ax2 = axes[0, 1]
    for k, c in zip(layers_to_plot, colors):
        ax2.plot(nh4[k, mid_j, :], xc, '-o', color=c, label=f'Layer {k}', markersize=3)
    ax2.set_xlabel('氨氮 (gN/m³)')
    ax2.set_ylabel('X (m)')
    ax2.set_title('氨氮垂直分布')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 溶解氧垂直分布
    ax3 = axes[1, 0]
    for k, c in zip(layers_to_plot, colors):
        ax3.plot(o2[k, mid_j, :], xc, '-o', color=c, label=f'Layer {k}', markersize=3)
    ax3.set_xlabel('溶解氧 (gO₂/m³)')
    ax3.set_ylabel('X (m)')
    ax3.set_title('溶解氧垂直分布')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 氮磷比
    ax4 = axes[1, 1]
    po4 = nc.variables['abiotic_water_sPO4W'][0, :, :, :]
    np_ratio = (no3 + nh4) / (po4 + 1e-10)
    for k, c in zip(layers_to_plot, colors):
        ax4.plot(np_ratio[k, mid_j, :], xc, '-o', color=c, label=f'Layer {k}', markersize=3)
    ax4.set_xlabel('N/P 比')
    ax4.set_ylabel('X (m)')
    ax4.set_title('氮磷比垂直分布')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('figure_02_vertical_profiles.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    print("图2: 垂直剖面已保存")
    
    # 图3: 水动力场
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle('GETM 水动力场 - 表层', fontsize=14)
    
    u = nc.variables['uu'][0, 0, :, :]
    v = nc.variables['vv'][0, 0, :, :]
    w = nc.variables['w'][0, :, mid_j, :]
    
    # 流场矢量图
    ax1 = axes[0]
    skip = 2
    X, Y = np.meshgrid(xc, yc)
    ax1.quiver(X[::skip, ::skip], Y[::skip, ::skip], 
               u[::skip, ::skip], v[::skip, ::skip],
               np.sqrt(u[::skip, ::skip]**2 + v[::skip, ::skip]**2),
               cmap='viridis', scale=5)
    ax1.set_xlabel('X (m)')
    ax1.set_ylabel('Y (m)')
    ax1.set_title('表层流场')
    
    # 垂向流速
    ax2 = axes[1]
    im2 = ax2.contourf(xc, sigma, w.T, cmap='RdBu_r')
    ax2.set_xlabel('X (m)')
    ax2.set_ylabel('Sigma Layer')
    ax2.set_title('垂向流速 (m/s) - Y中心剖面')
    plt.colorbar(im2, ax=ax2)
    
    # 湍动能
    tke = nc.variables['tke'][0, :, mid_j, :]
    ax3 = axes[2]
    im3 = ax3.contourf(xc, sigma, tke.T, cmap='YlOrRd')
    ax3.set_xlabel('X (m)')
    ax3.set_ylabel('Sigma Layer')
    ax3.set_title('湍动能 TKE (m²/s²)')
    plt.colorbar(im3, ax=ax3)
    
    plt.tight_layout()
    plt.savefig('figure_03_hydrodynamics.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    print("图3: 水动力场已保存")
    
    nc.close()
    print("可视化完成!")

if __name__ == '__main__':
    plot_3d_results()
