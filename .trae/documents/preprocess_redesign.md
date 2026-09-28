# 前处理界面重做：湖泊边界 + 底部高程 + 网格生成 + 自动水深插值

## Context

当前"输入数据"页（[index.html#L116-L134](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/app/templates/index.html#L116-L134)）只是静态文件清单，用户无法从零创建模型：看不到数据格式要求、不能上传湖泊边界、不能生成网格、不能自动插值水深。后端 [server.py#L698-L735](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/app/server.py#L698-L735) 只返回 9 个固定文件清单。`3DWET/preprocessor/` 目录已有算法生成器（[generate_bathymetry.py](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/preprocessor/generate_bathymetry.py)），但用 LakeConfig 编程生成，不支持外部 shapefile 输入。

用户要求：新建一个独立的"前处理"页面，包含 4 个选项卡——湖泊边界、底部高程、网格生成、保存预览，支持 shapefile 多文件上传（点/面几何两种）、UTM 和 WGS84 经纬度两种坐标系、用户自定义网格大小、自动水深插值、流程内新建案例。

约束：不引入 geopandas/shapely/GDAL，仅用 pyshp + numpy + scipy + netCDF4（均已安装）。不修改 preprocessor/ 现有脚本，不删除 .p2d 数据。

## 实现方案

### 后端（[app/server.py](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/app/server.py) 追加，不动现有代码）

**新增模块级缓存**（约在 L33 之后）：
```python
_preprocess_cache = {"boundary": {}, "bathymetry": {}, "grid": {}}
def _new_cache_id(prefix): return f"{prefix}_{uuid.uuid4().hex[:8]}"
```

**新增端点（追加到 server.py 末尾，约 L1700 后）**：

1. `POST /api/preprocess/case/create`
   - body: `{case_name}`，创建 `case/<case_name>/`，调用现有 load_case 逻辑激活
   - 返回 `{success, case_name, case_path}`

2. `POST /api/preprocess/boundary/upload`
   - multipart 字段 `files`（多文件 .shp/.shx/.dbf/.prj，用 `request.files.getlist("files")`）
   - 保存到临时目录，用 `shapefile.Reader` 读取
   - 解析 .prj 文本（正则识别 `UTM`/`Transverse_Mercator`/`WGS_84`/`geographic`），返回 crs_type
   - 提取第一个 polygon 的外环坐标列表
   - 若是 geographic 坐标，整体转为简化 UTM（用纯 Python 公式：`x = (lon - zone_central)*111320*cos(lat)`，zone 由经度算）
   - 缓存 boundary，返回 `{boundary_id, n_points, bbox: [xmin,ymin,xmax,ymax], crs_type, utm_zone?, coords_preview}`

3. `POST /api/preprocess/bathymetry/upload`
   - multipart `files` + form 字段 `depth_field`
   - 用 `reader.shapeType` 判断 POINT(=1) / POLYGON(=5)
   - POINT: 提取 `[(x, y, depth), ...]`（depth 来自 `record[depth_field]`）
   - POLYGON: 提取 `[(polygon_coords, depth), ...]`
   - 同 boundary 做 CRS 转换（与 boundary 保持同一坐标系）
   - 返回 `{bathy_id, geom_type, n_features, depth_range: [min,max], fields: [...], crs_type}`

4. `POST /api/preprocess/grid/generate`
   - body: `{boundary_id, dx, dy, x0?, y0?, nx?, ny?}`
   - 若未给 nx/ny，从 boundary bbox 自动算：`nx = ceil((xmax-xmin)/dx)`，ny 同
   - 生成 cell-center 坐标 `xc[i] = x0 + (i+0.5)*dx`，`yc[j] = y0 + (j+0.5)*dy`
   - 对每个 cell center 调用现有 `_point_in_polygon`（[server.py#L1629](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/app/server.py#L1629)）生成 mask
   - 返回 `{grid_id, nx, ny, dx, dy, x0, y0, mask, n_water_cells, lake_area}`

5. `POST /api/preprocess/bathymetry/interpolate`
   - body: `{grid_id, bathy_id, method: 'nearest'|'linear'|'polygon'}`
   - POINT 几何：用 `scipy.interpolate.griddata`（已装 scipy）插值到 cell centers，水域 mask 外置 -9999
   - POLYGON 几何：逐 cell center 用 `_point_in_polygon` 找所在多边形取 depth
   - 返回 `{depth_array, n_water, depth_min, depth_max, depth_mean}`

6. `POST /api/preprocess/save`
   - body: `{case_name, grid_id, depth_array, lat0, lon0, lake_name}`
   - 写 `case/<case_name>/bathymetry.nc`，复用 [preprocessor/generate_bathymetry.py#L139-L194](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/preprocessor/generate_bathymetry.py#L139-L194) 的 `_write_bathymetry_nc` 逻辑（同款：grid_type=1，x/y UTM 米，latc/lonc 用简化公式，bathymetry 变量 + CF 属性）
   - 返回 `{success, path, n_water_cells}`

7. `GET /api/preprocess/preview?id=<boundary_id|grid_id>`
   - 返回缓存数据的精简版供前端 canvas 绘制

8. `GET /api/preprocess/help`
   - 返回 shapefile 格式说明 JSON：边界要求（Polygon shapefile，外环=湖岸线）、水深点要求（Point，必须有一个数值字段表示深度 m）、水深面要求（Polygon，每个多边形带 depth 属性）、CRS 要求（UTM 推荐；WGS84 也支持但精度略降）

### 前端

**[app/templates/index.html](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/app/templates/index.html) 修改**：

- L26-L31 导航"前处理"区新增一项：
  ```html
  <div class="nav-item" data-page="preprocess"><span class="nav-icon">🛠️</span>前处理</div>
  ```
- L115 之后新增 `page-preprocess` 页面：4 个 tab，每个 tab 上传控件 + Canvas 预览 + 格式说明卡片
- L11 引入 `preprocess.js`（在 app.js 之前）

**新建 [app/static/js/preprocess.js](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/app/static/js/preprocess.js)**：
- `initPreprocess()` - 初始化 tab 切换
- `uploadBoundary()` / `uploadBathymetry()` - FormData 多文件上传，调端点 2/3
- `generateGrid()` - 调端点 4
- `interpolateDepth()` - 调端点 5
- `saveBathymetry()` - 调端点 1+6，新建案例后写入
- `drawBoundaryPreview()` / `drawBathymetryPreview()` / `drawGridPreview()` / `drawDepthPreview()` - Canvas 2D 绘制（沿用 [app.js#L811-L842 drawHeatmap](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/app/static/js/app.js#L811-L842) 思路：cellW/cellH + fillRect）
- `state.preprocess = {boundary_id, bathy_id, grid_id, depth_array}` 状态管理

**[app/static/js/app.js#L70-L82 navigate()](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/app/static/js/app.js#L70-L82) 修改**：
- titles 字典加 `preprocess:'前处理'`
- 增加 `if (page === 'preprocess') initPreprocess();`

**[app/static/css/style.css](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/app/static/css/style.css) 追加**（沿用 L215-L218 的 .tab 样式扩展）：
- `.preprocess-tabs`、`.preprocess-tab`、`.preprocess-tab.active`
- `.upload-zone`（虚线边框 + hover 高亮）
- `.format-help-card`（提示卡片）
- `.preview-canvas-wrap`（Canvas 容器，固定 aspect ratio）

### 关键技术点

- **pyshp 多文件读取**：必须先保存 .shp/.shx/.dbf 到同一临时目录，再 `shapefile.Reader(temp_dir + "/x.shp")`，pyshp 会自动找 .shx/.dbf
- **.prj 解析**：用正则匹配 PROJCS/GEOGCS 名称，识别 UTM zone（central_meridian 推 zone = floor((central_meridian + 183) / 6)）
- **latlon→UTM 简化**：`x_utm = 500000 + (lon - zone_central_meridian) * 111320 * cos(lat_rad)`，`y_utm = (lat - 0) * 110574` —— 精度约 ±100m，对湖泊网格建模足够
- **网格 mask**：直接复用 `_point_in_polygon` 函数（[server.py#L1629](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/app/server.py#L1629)）
- **水深插值**：`scipy.interpolate.griddata(points, values, cell_centers, method='linear')`，水域外强制 -9999
- **bathymetry.nc 写入**：直接借用 [preprocessor/generate_bathymetry.py#L139-L194 _write_bathymetry_nc](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/preprocessor/generate_bathymetry.py#L139-L194) 的格式（grid_type=1、x/y UTM 米、latc/lonc 简化公式、bathymetry 变量 + standard_name="sea_floor_depth"）。在 server.py 内重新实现一份（避免 preprocessor 模块的 LakeConfig 依赖）

## 修改文件清单

| 文件 | 改动 |
|---|---|
| [app/server.py](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/app/server.py) | 顶部加 `_preprocess_cache`、`import shapefile`；末尾追加 8 个新端点 + 辅助函数（约 350 行） |
| [app/templates/index.html](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/app/templates/index.html) | L26-L31 加导航项；L115 后新增 `page-preprocess` 页面（约 100 行 HTML） |
| [app/static/js/preprocess.js](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/app/static/js/preprocess.js) | 新建（约 300 行 JS） |
| [app/static/js/app.js](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/app/static/js/app.js) | navigate() 函数加 preprocess 分支 + titles 字典（3 行） |
| [app/static/css/style.css](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/app/static/css/style.css) | 追加 preprocess 相关样式（约 50 行） |

## 不做的事

- 不修改骆马湖 .p2d 数据
- 不修改 preprocessor/ 目录现有脚本
- 不引入 geopandas/shapely/GDAL/pyproj
- 不动 viz2d 现有渲染逻辑（"看不到网格"靠前处理页的 Canvas 预览解决；如果用户希望 viz2d 在无 NC 输出时也显示 bathymetry 网格，作为后续单独任务）

## 验证

1. 启动 Flask：`python app/server.py`（已在 http://127.0.0.1:8766 运行，热重载）
2. 临时生成测试 shapefile（一个简单椭圆 polygon + 若干散点水深），用 pyshp 在 `case/_preprocess_test/` 写一个小脚本
3. 浏览器进入 http://127.0.0.1:8766 → 侧栏"前处理" → 4 个 tab 依次操作：
   - 上传边界 shapefile → Canvas 显示多边形
   - 上传水深 shapefile → 显示散点/多边形 + depth 范围
   - 输入 dx=100, dy=100 → 生成网格，预览叠加图，水域格数正确
   - 选插值方法 → 预览 depth 热图 → 输入案例名 → 保存
4. 用 Python 验证 `ncdump -h case/<new>/bathymetry.nc`：grid_type=1，x/y/latc/lonc/bathymetry 变量齐全，shape 正确
5. 进入"案例管理"加载新案例 → 进入"输入数据"页 → bathymetry.nc 显示存在
6. 进入"2D 可视化"页（无 NC 输出时仍空白——这是已知限制，不在本次范围）
