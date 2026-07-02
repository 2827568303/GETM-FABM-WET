# WET 工具函数 (utility.F90)

> **源文件**: [3DWET/src/wet/src/utility.F90](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/src/wet/src/utility.F90)
> **模块名**: `wet_utility`
> **作用**: 提供 WET 所有模块共用的温度函数、日长函数、氧饱和度函数

---

## 1. 全局常数

| 常数 | 值 | 说明 |
|------|-----|------|
| `cTmRef` | 20.0 ℃ | 参考温度（所有温度函数的基准） |
| `Pi` | 3.14159265358979 | 圆周率 |
| `deg2rad` | Pi/180 | 度→弧度转换 |
| `ecliptic` | 23.439° × deg2rad | 黄赤交角 |

---

## 2. 温度依赖函数

WET 提供三种温度依赖函数，各模块按需选用。

### 2.1 Arrhenius 型（指数型）
**函数**: `uFunTmArrh(uTm, cTheta)` ([utility.F90 L27-35](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/src/wet/src/utility.F90#L27-L35))

$$f(T) = \theta^{T - T_{ref}}$$

- **参数**: `cTheta` (θ) — 温度系数，典型值 1.02~1.11
- **特点**: 单调递增，无最适温度，适用于矿化、硝化等持续增强的过程
- **使用模块**: abiotic_water (硝化、硅矿化)、abiotic_sediment、om_pool、zoobenthos 等

### 2.2 Gaussian 型（最适温度型）
**函数**: `uFunTmGaus(uTm, cSigTm, cTmOpt)` ([utility.F90 L40-48](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/src/wet/src/utility.F90#L40-L48))

$$f(T) = \exp\left(-\frac{1}{2\sigma^2}\left[(T - T_{opt})^2 - (T_{ref} - T_{opt})^2\right]\right)$$

- **参数**: `cSigTm` (σ) — 温度标准差；`cTmOpt` (Topt) — 最适温度
- **特点**: 钟形曲线，有最适温度，高于最适温度时降低
- **使用模块**: phytoplankton、macrophytes、fish 等

### 2.3 Q10 型（植物型）
**函数**: `uFunTmQ10(uTm, cQ10Veg)` ([utility.F90 L53-61](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/src/wet/src/utility.F90#L53-L61))

$$f(T) = Q_{10}^{0.1(T - T_{ref})}$$

- **参数**: `cQ10Veg` (Q10) — 温度每升高 10℃ 反应速率的倍数
- **特点**: 类似 Arrhenius 但用 Q10 表达，适用于植物
- **使用模块**: macrophytes

---

## 3. 日长函数

**函数**: `DayLength(latitude, day)` ([utility.F90 L66-81](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/src/wet/src/utility.F90#L66-L81))

$$m = 1 - \tan(\text{lat} \cdot \text{deg2rad}) \cdot \tan(\varepsilon \cdot \cos(0.0172 \cdot \text{day}))$$

$$\text{DayLength} = \frac{\arccos(1 - m)}{\pi}$$

- **输入**: `latitude` (纬度，度)、`day` (年积日，1-365)
- **输出**: 日长占全天的比例（0~1），乘以 24 得小时数
- **来源**: http://www.gandraxa.com/length_of_day.xml
- **用途**: macrophytes 的季节性计算

---

## 4. 氧饱和度函数

**函数**: `uFunO2Sat(salt, temp)` ([utility.F90 L86-101](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/src/wet/src/utility.F90#L86-L101))

$$T_{abs} = T + 273.15$$

$$a = -173.4292 + 249.6339 \cdot \frac{100}{T_{abs}} + 143.3483 \cdot \ln\left(\frac{T_{abs}}{100}\right)$$

$$b = 21.8492 \cdot \frac{T_{abs}}{100}$$

$$c = S \cdot \left(-0.033096 + 0.014259 \cdot \frac{T_{abs}}{100} - 0.0017 \cdot \left(\frac{T_{abs}}{100}\right)^2\right)$$

$$O_{2,sat} = 1.42763 \cdot \exp(a - b + c) \quad [\text{g/m}^3]$$

- **来源**: Riley & Skirrow (1974)，AED2 实现
- **输入**: `salt` (盐度 PSU)、`temp` (温度 ℃)
- **特点**: 同时考虑温度和盐度对氧饱和度的影响

---

## 5. PCLake 对比说明

| 函数 | WET 实现 | PCLake 实现 | 差异 |
|------|---------|------------|------|
| Arrhenius | `θ^(T-20)` | 同 | 无 |
| Gaussian | `exp(-0.5/σ²·((T-Topt)²-(20-Topt)²))` | 同 | 无 |
| Q10 | `Q10^(0.1·(T-20))` | 同 | 无 |
| O2饱和度 | Riley & Skirrow (1974)，含盐度修正 | 简化公式（仅温度） | **WET 含盐度修正，PCLake 通常用纯淡水公式** |
| 日长 | 基于纬度+年积日解析式 | 同 | 无 |

> **待对比**: PCLake+Gras 的氧饱和度公式需要从 derivatives sheet 中提取 `_uO2Sat_` 行确认。
