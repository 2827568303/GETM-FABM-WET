# 3DWET 项目开发规范

**版本**: v1.0  
**更新日期**: 2026-07-02  
**适用范围**: 3DWET 三维水生态模型项目所有开发工作

---

## 一、云端开发架构

### 1.1 整体架构

```
┌──────────────────────────────────────────────────────┐
│                    GitHub 仓库                        │
│           (代码唯一真实来源，私有仓库)                 │
│      https://github.com/dinod520/GETM-FABM-WET       │
└──────────────┬───────────────────┬───────────────────┘
               │                   │
               │ git pull/push     │ git pull/push
               │                   │
    ┌──────────▼──────┐   ┌────────▼──────────┐
    │  云端开发环境    │   │   本地 Windows     │
    │  (TRAE / 云主机) │   │   (WSL2 + Ubuntu)  │
    │  - 写代码        │   │  - 写代码          │
    │  - 编译调试      │   │  - 编译调试        │
    │  - 小算例测试    │   │  - 大算例运行      │
    └──────────────────┘   └────────────────────┘
```

### 1.2 核心原则

1. **GitHub 是唯一真相源** —— 所有代码通过 Git 同步，不用 U盘/网盘传文件
2. **编译产物不入仓库** —— build/、install/、*.nc 等大文件全部由 .gitignore 排除
3. **多设备开发一致** —— 每台设备从同一仓库拉取，用同一套构建脚本
4. **先 pull 再开发** —— 每次开始工作前先拉取最新代码

---

## 二、环境要求

### 2.1 编译工具链

| 工具 | 最低版本 | 说明 |
|------|----------|------|
| GCC/gfortran | >= 13.0 | C 和 Fortran 编译器 |
| CMake | >= 3.10 | 构建系统 |
| make | - | 构建工具 |
| NetCDF-C | >= 4.0 | NetCDF C 库 |
| NetCDF-Fortran | >= 4.0 | NetCDF Fortran 绑定 |
| Python | >= 3.8 | 可视化和工具脚本 |

### 2.2 各平台安装方式

#### Ubuntu / WSL2 / TRAE 云端环境
```bash
sudo apt update
sudo apt install -y build-essential gfortran cmake make \
    libnetcdf-dev libnetcdff-dev netcdf-bin python3 python3-pip
```

#### Windows (通过 WSL2)
1. 安装 WSL2: `wsl --install -d Ubuntu`
2. 进入 WSL 后执行上述 Ubuntu 安装命令

### 2.3 验证环境
```bash
gfortran --version      # 应显示 13.x
cmake --version         # 应显示 3.10+
nf-config --version     # 应显示 4.x
nc-config --version     # 应显示 4.x
```

---

## 三、项目目录结构

```
GETM-FABM-WET/
├── .gitignore                      # Git 忽略规则
├── 3DWET/                          # 项目主目录
│   ├── src/                        # 源代码
│   │   ├── getm/                   # GETM 三维水动力模型
│   │   ├── fabm/                   # FABM 生物地球化学框架
│   │   ├── gotm/                   # GOTM 湍流模型
│   │   └── wet/                    # WET/PCLake 生态模型
│   ├── patches/                    # Bug 修复补丁
│   ├── scripts/                    # 脚本工具
│   │   ├── build/                  # 编译脚本
│   │   ├── data_gen/               # 数据生成脚本
│   │   ├── analysis/               # 分析诊断脚本
│   │   ├── visualize/              # 可视化脚本
│   │   ├── debug/                  # 调试脚本
│   │   ├── fix/                    # 修复脚本
│   │   ├── config/                 # 配置文件模板
│   │   ├── theoretical_lake/       # 理论湖专用脚本
│   │   └── build_model.sh          # 主编译脚本
│   ├── cases/                      # 测试案例
│   │   ├── theoretical_lake/       # 理论湖基准测试
│   │   ├── luomahu/                # 骆马湖案例
│   │   └── yilong/                 # 异龙湖案例
│   ├── cmake/                      # CMake 模块 (FindNetCDF.cmake 等)
│   ├── docs/                       # 项目文档
│   ├── app/                        # Web 应用
│   ├── viewer/                     # 可视化查看器
│   ├── build/                      # 编译输出 (.gitignore 排除)
│   └── install/                    # 安装输出 (.gitignore 排除)
└── README.md
```

---

## 四、Git 工作流

### 4.1 分支策略

采用简化的 Git Flow 模型：

| 分支 | 用途 | 命名规范 | 生命周期 |
|------|------|---------|---------|
| `main` | 稳定发布版本 | 固定 | 永久 |
| `develop` | 日常开发集成分支 | 固定 | 永久 |
| `feature/*` | 新功能开发 | `feature/草鱼模块` | 合并后删除 |
| `bugfix/*` | Bug 修复 | `bugfix/硅藻峰值过高` | 合并后删除 |
| `hotfix/*` | 紧急修复（基于 main） | `hotfix/段错误修复` | 合并后删除 |

### 4.2 分支使用规则

```bash
# 日常开发在 develop 分支
git checkout develop
git pull origin develop

# 新功能开分支
git checkout -b feature/grass-carp develop

# 开发完成后合并
git checkout develop
git merge --no-ff feature/grass-carp
git push origin develop

# 删除功能分支
git branch -d feature/grass-carp
```

### 4.3 紧急修复流程

```bash
# 从 main 创建 hotfix 分支
git checkout main
git checkout -b hotfix/critical-crash

# 修复后合并到 main 和 develop
git checkout main
git merge --no-ff hotfix/critical-crash
git push origin main

git checkout develop
git merge --no-ff hotfix/critical-crash
git push origin develop

git branch -d hotfix/critical-crash
```

---

## 五、提交规范

### 5.1 Commit Message 格式

```
<类型>(<范围>): <简要描述>

<详细说明（可选）>
```

### 5.2 类型定义

| 类型 | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat(fish): 添加草鱼模块` |
| `fix` | Bug 修复 | `fix(getm_fabm): 修复 itime 参数传递` |
| `refactor` | 重构 | `refactor(scripts): 整理脚本目录结构` |
| `docs` | 文档更新 | `docs: 更新编译指南` |
| `style` | 代码格式 | `style: 统一缩进` |
| `test` | 测试相关 | `test: 添加水平衡验证脚本` |
| `chore` | 构建/工具 | `chore: 更新 .gitignore` |
| `perf` | 性能优化 | `perf: 启用 OpenMP 多线程` |

### 5.3 提交规则

1. **每次提交只做一件事** —— 不要把多个不相关的修改放一个 commit
2. **描述用中文** —— 项目面向中国湖泊场景，中文更直观
3. **不说废话** —— "修改了文件"这种描述没有意义
4. **提交前检查** —— `git status` 和 `git diff` 看清楚要提交什么

### 5.4 示例

```bash
# 好的提交
git commit -m "feat(fish): 添加草鱼模块，含3个状态变量和16个参数"
git commit -m "fix(getm_fabm): 修复 itime 未传递导致浮游植物光照耦合失败"
git commit -m "refactor(scripts): 将根目录脚本整理到 scripts/ 子目录"

# 不好的提交
git commit -m "更新"
git commit -m "修改了一些文件"
git commit -m "fix bug"
```

---

## 六、编译与运行

### 6.1 编译流程

```bash
# 进入项目目录
cd 3DWET

# 一键编译（自动应用补丁、编译 FABM+GETM、安装）
bash scripts/build_model.sh

# 编译产物在 install/bin/getm_cartesian
```

### 6.2 编译顺序（手动编译时）

```
1. 应用补丁 → 2. 编译 FABM (+WET) → 3. 应用 GETM 补丁 → 4. 编译 GETM → 5. 恢复源文件
```

**重要**：必须先编译 FABM（含 WET），再编译 GETM，因为 GETM 依赖 FABM 库。

### 6.3 运行测试

```bash
# 进入案例目录
cd cases/theoretical_lake

# 运行模型
../../install/bin/getm_cartesian

# 运行可视化
python3 ../../scripts/visualize.py
```

### 6.4 编译问题排查

| 问题 | 解决方案 |
|------|---------|
| `Could not find NetCDF` | 确认已安装 libnetcdf-dev 和 libnetcdff-dev |
| `gfortran not found` | 安装 gfortran: `apt install gfortran` |
| `FABM not found` | 先编译 FABM，确认 install/fabm/ 目录存在 |
| `gotm/src not found` | 确认 GOTM 源码已下载到 3DWET/src/gotm/ |
| `wet/src not found` | 确认 WET 源码已下载到 3DWET/src/wet/ |
| 编译器名不匹配 | build_model.sh 会自动检测 gcc-13 或 gcc |

---

## 七、发布流程

### 7.1 版本号规范

采用语义化版本：`MAJOR.MINOR.PATCH`

| 变化 | 示例 |
|------|------|
| MAJOR | 架构变更（如新增草鱼模块）: v1.0 → v2.0 |
| MINOR | 功能增强（如新增案例）: v1.0 → v1.1 |
| PATCH | Bug 修复（如修参数）: v1.0.1 → v1.0.2 |

### 7.2 发布步骤

```bash
# 1. 确认 develop 分支稳定
git checkout develop
git pull origin develop

# 2. 创建发布分支
git checkout -b release/v1.1 develop

# 3. 更新版本号和文档
# 修改 README.md 中的版本号
# 更新 CHANGELOG

# 4. 合并到 main
git checkout main
git merge --no-ff release/v1.1
git push origin main

# 5. 打 tag
git tag -a v1.1 -m "3DWET v1.1: 添加草鱼模块"
git push origin v1.1

# 6. 合并回 develop
git checkout develop
git merge --no-ff release/v1.1
git push origin develop

# 7. 删除发布分支
git branch -d release/v1.1
```

### 7.3 发布检查清单

发布前必须确认：
- [ ] 所有测试案例运行通过
- [ ] 编译无 warning（或 warning 已知且可接受）
- [ ] README.md 版本号已更新
- [ ] CHANGELOG 已更新
- [ ] .gitignore 未遗漏新的产物类型
- [ ] install/bin/getm_cartesian 可正常执行

---

## 八、多设备开发操作手册

### 8.1 新设备首次配置

```bash
# 1. 安装编译工具链（见第二节）

# 2. Clone 仓库
git clone https://github.com/dinod520/GETM-FABM-WET.git
cd GETM-FABM-WET

# 3. 配置 Git 身份（如果还没配过）
git config user.name "你的名字"
git config user.email "你的邮箱"

# 4. 编译
cd 3DWET
bash scripts/build_model.sh

# 5. 验证
cd cases/theoretical_lake
../../install/bin/getm_cartesian
```

### 8.2 日常开发流程

```bash
# 开始工作前：拉取最新代码
git pull origin develop

# 写代码、改参数、调试...

# 编译测试
cd 3DWET && bash scripts/build_model.sh

# 运行测试
cd cases/theoretical_lake && ../../install/bin/getm_cartesian

# 提交代码
git add <具体文件>
git commit -m "fix(phyto): 调整硅藻 cMuMax 参数"
git push origin develop
```

### 8.3 换设备继续工作

```bash
# 在新设备上
git pull origin develop

# 如果改了 Fortran 代码，重新编译
cd 3DWET && bash scripts/build_model.sh

# 继续...
```

### 8.4 冲突处理

```bash
# 拉取时遇到冲突
git pull origin develop
# Auto-merging xxx.F90
# CONFLICT (content): Merge conflict in xxx.F90

# 查看冲突文件
git status

# 手动解决冲突后
git add xxx.F90
git commit -m "merge: 合并 develop 分支，解决 xxx.F90 冲突"
git push origin develop
```

---

## 九、数据文件管理

### 9.1 入库规则

| 文件类型 | 入库 | 说明 |
|---------|------|------|
| 源代码 (.F90, .py, .sh) | ✅ | 必须入库 |
| 配置文件 (.yaml, .inp, .nml) | ✅ | 必须入库 |
| 文档 (.md) | ✅ | 必须入库 |
| 编译产物 (.o, .mod, .a) | ❌ | .gitignore 排除 |
| 数据文件 (.nc, .h5) | ❌ | .gitignore 排除 |
| 运行日志 (.log) | ❌ | .gitignore 排除 |
| 备份文件 (.bak) | ❌ | .gitignore 排除 |
| 图表文件 (.png) | ✅ | 可入库（结果图有参考价值） |
| Excel 文件 (.xls) | ⚠️ | 仅入库输入数据模板 |

### 9.2 大文件处理

如果数据文件超过 50MB：
1. 不要提交到 Git
2. 使用网盘/对象存储单独管理
3. 在 README 中记录数据文件来源和下载方式

---

## 十、注意事项

### 10.1 禁止事项

1. **不要直接在 main 分支开发** —— 通过 develop 或 feature 分支
2. **不要提交编译产物** —— build/ 和 install/ 目录已排除
3. **不要提交大文件** —— .nc 数据文件不入库
4. **不要删除 patches/ 目录** —— 补丁文件是编译必需的
5. **不要修改 src/ 下的第三方源码** —— 通过 patch 机制修改

### 10.2 补丁管理

第三方代码（GETM、FABM、GOTM、WET）的修改通过 patch 文件管理：
- patch 文件存放在 `3DWET/patches/`
- `build_model.sh` 编译时自动应用
- 编译完成后自动恢复原始源码
- 这样保持上游源码可追溯，便于未来升级

### 10.3 测试规范

修改代码后，按层次测试：
1. **2D 水动力测试** —— 验证水流、水位
2. **3D + GOTM 测试** —— 验证温度、湍流
3. **FABM-WET 完整测试** —— 验证生态过程
4. **对比基线** —— 与之前版本结果对比

---

## 附录

### A. 常用 Git 命令

```bash
# 查看状态
git status

# 查看修改内容
git diff

# 查看提交历史
git log --oneline -10

# 撤销修改（未 add 的）
git checkout -- <file>

# 撤销 add（已 add 未 commit 的）
git reset HEAD <file>

# 撤销最近一次 commit（保留修改）
git reset --soft HEAD~1

# 创建并切换分支
git checkout -b <branch-name>

# 合并分支
git merge <branch-name>

# 打标签
git tag -a v1.0 -m "版本说明"
```

### B. 相关文档

| 文档 | 位置 | 用途 |
|------|------|------|
| README.md | 3DWET/ | 项目简介与快速入门 |
| USER_GUIDE.md | 3DWET/docs/ | 用户使用手册 |
| MODEL_MODULES.md | 3DWET/docs/ | 模型源代码模块说明 |
| COMPILE_GUIDE.md | 3DWET/docs/ | 编译指南 |
| PROJECT_SUMMARY.md | 3DWET/docs/ | 项目总结报告 |
| 本文档 | 3DWET/docs/ | 开发规范与云端协作 |

---

**文档版本**: v1.0  
**最后更新**: 2026-07-02
