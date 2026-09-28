# 3DWET Web 系统报错检查与修复记录

**日期**: 2026-08-18
**检查范围**: `app/启动Web系统.bat` → `app/server.py` → 模型调用全链路

---

## 一、发现的问题及修复

### BUG-1: 逻辑值被加引号导致 Fortran namelist 解析崩溃（致命）

**现象**: 模型启动即崩溃，报错：
```
At line 175 of initialise.F90 (unit = 10, file = './/getm.inp')
Fortran runtime error: Cannot match namelist object name '.false.'
```

**根因**: `write_getm_inp()` 函数将所有字符串值用单引号包裹，包括 Fortran 逻辑值 `.true.` / `.false.`。Fortran namelist 规范要求逻辑值**不加引号**，写成 `.false.` 而非 `'.false.'`。加引号后解析器将其视为字符串，导致后续 token 错位。

**修复**:
- `parse_getm_inp()`: 新增逻辑值识别，将 `.true.`/`.false.` 解析为 Python `bool`
- `write_getm_inp()`: `bool` 类型输出为 `.true.`/`.false.`（无引号），仅字符串类型加引号

```python
# 修复后
if isinstance(val, bool):
    f.write(f"   {key} = .{'true' if val else 'false'}.\n")
elif isinstance(val, str):
    f.write(f"   {key} = '{val}'\n")
```

---

### BUG-2: 配置文件写入 CRLF 行尾导致 WSL 中 Fortran 无法解析（致命）

**现象**: 同 BUG-1 的 namelist 解析错误，即使逻辑值格式正确也可能出现。

**根因**: Python `open()` 在 Windows 上默认使用 CRLF (`\r\n`) 行尾。WSL/Linux 中的 GNU Fortran 运行时无法正确处理 CRLF，将 `\r` 视为 token 的一部分。

**修复**: `write_getm_inp()` 打开文件时指定 `newline="\n"`，强制 LF 行尾。

```python
with open(filepath, "w", encoding="utf-8", newline="\n") as f:
```

---

### BUG-3: `step_2d` 被写入错误的 namelist（致命）

**现象**: 模型报错：
```
At line 100 of time.F90 (unit = 10, file = './/getm.inp')
Fortran runtime error: Cannot match namelist object name step_2d
```

**根因**: `config_time()` 端点将 `step_2d` 写入 `&time` namelist，但 GETM 源码中 `&time` 只接受 `timestep, timefmt, nlast, start, stop`。`step_2d` 和 `step_3d` 属于 `&io_spec` namelist。

**修复**:
- `get_time_settings()`: 从 `io_spec` 读取 `step_2d`/`step_3d`
- `config_time()` POST 处理: 将 `step_2d`/`step_3d` 写入 `config["io_spec"]` 而非 `config["time"]`

---

### BUG-4: WSL 命令中路径含空格未加引号（致命）

**现象**: 案例目录名含空格（如 "Theoretical lake"）时，模型无法启动。

**根因**: `run_model_thread()` 构造的 WSL 命令为：
```python
cmd = ["wsl.exe", "bash", "-c", f"cd {case_wsl} && {exe_wsl}"]
```
`cd /mnt/c/.../Theoretical lake` 会被 bash 解析为 `cd /mnt/c/.../Theoretical` + 多余参数 `lake`。

**修复**: 路径加单引号：
```python
cmd = ["wsl.exe", "bash", "-c", f"cd '{case_wsl}' && '{exe_wsl}' > '{log_wsl}' 2>&1"]
```

---

### BUG-5: 无控制台环境下 stdout 无效导致服务器崩溃（严重）

**现象**: 通过 `Start-Process -WindowStyle Hidden` 或 `pythonw.exe` 启动时，服务器在首次 `print()` 时崩溃。

**根因**: 隐藏窗口模式下 Python 的 `sys.stdout`/`sys.stderr` 可能为 `None` 或无效，`print()` 抛出异常导致进程退出。

**修复**: 在路径初始化后添加 stdout/stderr 保护，当检测到无效控制台时自动重定向到日志文件：
```python
class _SafeLog:
    """Fallback stream that writes to a log file when console is unavailable."""
    ...
for _stream_name in ("stdout", "stderr"):
    _s = getattr(sys, _stream_name, None)
    if _s is None or not hasattr(_s, "write"):
        setattr(sys, _stream_name, _SafeLog(str(APP_DIR / f"server_{_stream_name}.log")))
```

---

### BUG-6: 子进程管道在 Windows 无控制台环境下导致服务器崩溃（严重）

**现象**: 模型运行约 40-70 秒后服务器进程整体崩溃，无 Python 异常日志。

**根因**: `subprocess.Popen` 使用 `stdout=subprocess.PIPE` 读取模型输出，在隐藏窗口模式下 Windows 控制台句柄继承存在问题，导致父进程崩溃。

**修复**:
1. 模型输出改为在 WSL/bash 内部重定向到日志文件（`> model_run.log 2>&1`），不通过 Python 管道
2. 添加 `creationflags=subprocess.CREATE_NO_WINDOW` 防止弹出控制台窗口
3. 服务器通过轮询日志文件获取实时进度

```python
cmd = ["wsl.exe", "bash", "-c",
       f"cd '{case_wsl}' && '{exe_wsl}' > '{log_wsl}' 2>&1"]
run_process = subprocess.Popen(
    cmd,
    creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
)
# 轮询日志文件获取进度
while run_process.poll() is None:
    time.sleep(1.0)
    # 读取新增日志行...
```

---

### BUG-7: `get_run_info()` 读取错误的 namelist（中等）

**现象**: Web 界面显示的运行信息（标题、层数等）不正确。

**根因**: 函数从不存在的 `project`、`m2d.nlev`、`hotstart`、`output` 等键读取值，而实际结构为 `param.title`、`m3d.M`、`param.hotstart`。

**修复**: 从正确的 namelist 读取：
```python
param = config.get("param", {})
m3d = config.get("m3d", {})
return {
    "title": param.get("title", "3DWET Run"),
    "runid": param.get("runid", "3DWET"),
    "nlev": m3d.get("M", 10),
    "hotstart": param.get("hotstart", False),
    "runtype": param.get("runtype", 4),
    ...
}
```

---

### BUG-8: 热启动配置读写错误的 namelist（中等）

**现象**: 热启动设置无法正确保存/读取。

**根因**: `config_hotstart()` 读写独立的 `&hotstart` namelist，但 GETM 中 `hotstart` 是 `&param` namelist 中的一个变量。

**修复**: 改为读写 `config["param"]["hotstart"]`。

---

### BUG-9: .bat 文件声称自动打开浏览器但未实现（轻微）

**现象**: .bat 输出"浏览器将自动打开..."但实际不会打开。

**修复**: 添加延迟启动浏览器的命令：
```bat
start /b "" cmd /c "timeout /t 3 /nobreak >nul 2>nul & start http://localhost:8766"
```

---

## 二、验证结果

### 修复前
- 服务器可启动，但通过 Web 界面保存配置后 getm.inp 格式被破坏
- 模型无法通过 Web 界面启动（namelist 解析错误）
- 隐藏窗口模式下服务器不稳定

### 修复后（全部通过）
| 测试项 | 结果 |
|--------|------|
| .bat 双击启动服务器 | ✅ 正常启动，浏览器自动打开 |
| 案例列表加载 | ✅ 显示 Lake Luoma、Theoretical lake |
| 案例加载与配置解析 | ✅ 时间设置、运行信息正确 |
| 配置保存（时间/热启动） | ✅ getm.inp 格式正确（逻辑值无引号、LF行尾、step_2d在io_spec） |
| 模型启动运行 | ✅ WSL 中 getm_cartesian 正常执行 |
| 实时进度显示 | ✅ 日志轮询显示 n=100,200,... 进度 |
| 模型完成 | ✅ 4天测试运行 69 秒完成，退出码 0 |
| 隐藏窗口模式稳定性 | ✅ 服务器在模型完成后仍存活 |
| 输出文件生成 | ✅ THEORETICAL_LAKE.2d.nc / .3d.nc 正常生成 |

### 测试环境
- 模型: getm_cartesian (GETM 2.5.0 + GOTM 7.0.0 + FABM/WET)
- 案例: Theoretical lake (24×20 网格, 10 层, 4天, 60s 步长)
- 服务器: Waitress 4线程, http://127.0.0.1:8766
- Python: Anaconda3 (C:\ProgramData\anaconda3\python.exe)

---

## 三、修改的文件清单

| 文件 | 修改内容 |
|------|----------|
| `app/server.py` | 修复 8 个 bug（逻辑值格式、行尾、namelist 归属、路径引号、stdout保护、子进程稳定性、配置读取） |
| `app/启动Web系统.bat` | 添加浏览器自动打开功能 |
| `case/Theoretical lake/getm.inp` | 修复逻辑值引号、移除 &time 中的 step_2d、恢复60天配置 |

---

## 四、使用方式

1. 双击 `app/启动Web系统.bat`
2. 等待 cmd 窗口显示"服务地址: http://localhost:8766"
3. 浏览器会在 3 秒后自动打开（如未打开，手动访问 http://localhost:8766）
4. 在网页中选择案例、配置参数、启动模型
5. 模型运行日志实时显示在网页中，完成后可可视化结果
6. **关闭 cmd 窗口即停止服务**
