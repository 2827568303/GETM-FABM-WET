# 3DWET - 三维水动力-水质-食物网模型

**3D Hydrodynamic-Water Quality-Food Web Model**

基于 GETM-FABM-WET/PCLake 耦合的完整三维湖泊生态系统模型。

---

## 简介

3DWET 是一个集成了水动力、水质和完整食物网的三维湖泊生态模型，由以下组件耦合而成：

- **GETM** - 三维水动力模型（水流、温度、输运）
- **GOTM** - 湍流模型（垂直混合）
- **FABM** - 生物地球化学框架（模型耦合）
- **WET/PCLake** - 全生态系统模型（水质、浮游生物、沉水植物、底栖生物、鱼类）

### 模型特色

- ✅ 完整的三维水动力模拟
- ✅ 水质模块（营养盐、溶解氧、有机质）
- ✅ 浮游植物（蓝藻、硅藻、绿藻）
- ✅ 浮游动物（枝角类、桡足类）
- ✅ 沉水植物模块
- ✅ 底栖生物模块
- ✅ 鱼类模块（三个功能群）
- ✅ 完整食物网相互作用

---

## 快速开始

### 1. 编译模型

```bash
cd 3DWET
bash scripts/build_model.sh
```

### 2. 运行模拟

```bash
cd case
../install/bin/getm_cartesian
```

### 3. 可视化结果

```bash
python ../scripts/visualize.py
```

---

## 目录结构

```
3DWET/
├── src/          # 源代码 (GETM, FABM, GOTM, WET)
├── patches/      # Bug 修复补丁
├── scripts/      # 编译和可视化脚本
├── case/         # 罗目湖测试用例
├── build/        # 编译目录（编译后生成）
├── install/      # 安装目录（编译后生成）
└── docs/         # 文档
    ├── MODEL_MODULES.md   # 模块详细说明
    └── USER_GUIDE.md      # 使用说明
```

---

## 文档

| 文档 | 说明 |
|------|------|
| [docs/USER_GUIDE.md](docs/USER_GUIDE.md) | 模型使用说明（入门必读） |
| [docs/MODEL_MODULES.md](docs/MODEL_MODULES.md) | 源代码和模块详细说明 |

---

## 系统要求

- GCC / gfortran 13+
- CMake 3.10+
- NetCDF-Fortran 4.5+
- Python 3.8+ (用于可视化)

详细安装说明请参考 [使用说明](docs/USER_GUIDE.md)。

---

## 已修复的 Bug

1. **gotm_fabm itime 可选参数问题** - 导致段错误
2. **fish check_state 数组越界** - qStage=0 时访问未注册变量
3. **om_pool 数组下标错误** - refractory POM 注册逻辑
4. **getm_fabm 耦合接口改进** - v2 补丁
5. **fabm.F90 DEBUG 输出** - 导致日志膨胀和性能下降（编译时自动移除）
6. **gotm_fabm.yaml 缺失** - 导致 FABM 模块不运行（已添加到 case 目录）
7. **文档变量名错误** - 浮游动物/鱼类变量后缀应为 `_sD`（非 `_sDW_PV`），已修正
8. **垂直层数说明不清** - 实际层数由 `kdum` 控制（层数=kdum+1），非 `M`，已补充说明

所有补丁在编译时自动应用。

---

## 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0 | 2026-06-30 | 初始发布，整理完成 |
| v1.1 | 2026-06-30 | 首次测试通过，添加 gotm_fabm.yaml，移除 DEBUG 输出 |
| v1.2 | 2026-06-30 | 重新测试通过，修正变量名文档，补充垂直层数说明 |

---

## 相关资源

- GETM 官网: https://getm.eu/
- FABM 官网: https://fabm.net/
- GOTM 官网: https://gotm.net/

---

**最后更新**: 2026-06-30
