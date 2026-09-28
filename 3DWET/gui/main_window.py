"""
3DWET Grid Editor - Main Window
Integrates grid view, tools, menus, and dock panels.
"""
import sys
from pathlib import Path
import numpy as np
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox,
    QDoubleSpinBox, QPushButton, QComboBox, QDockWidget, QListWidget,
    QListWidgetItem, QFileDialog, QMessageBox, QStatusBar, QToolBar,
    QAction, QActionGroup, QSlider, QGroupBox, QFormLayout, QSplitter,
    QFrame, QSizePolicy, QShortcut, QDialog, QDialogButtonBox, QLineEdit,
    QCheckBox, QMessageBox, QProgressBar
)
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QIcon, QKeySequence, QFont, QColor, QPainter, QPixmap, QLinearGradient, QFontDatabase

from grid_model import GridModel, LAND_VALUE
from grid_view import GridView, TOOL_PAN, TOOL_PAINT, TOOL_TOGGLE, TOOL_SMOOTH, TOOL_RIVER, TOOL_INFO, TOOL_FILL


class NewGridDialog(QDialog):
    """Dialog for creating a new blank grid."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("新建网格")
        self.setMinimumWidth(320)
        layout = QFormLayout(self)

        self.nx_spin = QSpinBox()
        self.nx_spin.setRange(2, 500)
        self.nx_spin.setValue(30)
        layout.addRow("X 方向格数:", self.nx_spin)

        self.ny_spin = QSpinBox()
        self.ny_spin.setRange(2, 500)
        self.ny_spin.setValue(20)
        layout.addRow("Y 方向格数:", self.ny_spin)

        self.dx_spin = QDoubleSpinBox()
        self.dx_spin.setRange(1, 100000)
        self.dx_spin.setValue(500)
        self.dx_spin.setSuffix(" m")
        layout.addRow("X 方向格宽:", self.dx_spin)

        self.dy_spin = QDoubleSpinBox()
        self.dy_spin.setRange(1, 100000)
        self.dy_spin.setValue(500)
        self.dy_spin.setSuffix(" m")
        layout.addRow("Y 方向格宽:", self.dy_spin)

        self.depth_spin = QDoubleSpinBox()
        self.depth_spin.setRange(0, 1000)
        self.depth_spin.setValue(3.0)
        self.depth_spin.setSuffix(" m")
        self.depth_spin.setToolTip("初始水深，0 = 全部陆地")
        layout.addRow("初始水深:", self.depth_spin)

        self.all_land_check = QCheckBox("全部为陆地（手动绘制水域）")
        layout.addRow("", self.all_land_check)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_params(self):
        return {
            'nx': self.nx_spin.value(),
            'ny': self.ny_spin.value(),
            'dx': self.dx_spin.value(),
            'dy': self.dy_spin.value(),
            'depth': 0 if self.all_land_check.isChecked() else self.depth_spin.value(),
        }


class ColorBarWidget(QWidget):
    """Vertical color bar legend."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(48)
        self.setMaximumWidth(55)
        self.cmap = None
        self.vmin = 0
        self.vmax = 10

    def set_range(self, vmin, vmax, cmap):
        self.vmin = vmin
        self.vmax = vmax
        self.cmap = cmap
        self.update()

    def paintEvent(self, event):
        if self.cmap is None:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w = self.width()
        h = self.height()
        bar_w = 18
        bar_x = 4
        bar_h = h - 30
        bar_y = 15

        from matplotlib.colors import Normalize
        norm = Normalize(vmin=self.vmin, vmax=self.vmax)
        for y in range(int(bar_h)):
            val = self.vmax - (y / bar_h) * (self.vmax - self.vmin)
            rgba = self.cmap(norm(val))
            color = QColor(int(rgba[0]*255), int(rgba[1]*255), int(rgba[2]*255))
            painter.setPen(color)
            painter.drawLine(bar_x, int(bar_y + y), bar_x + bar_w, int(bar_y + y))

        # Border
        painter.setPen(QColor(150, 150, 150))
        painter.drawRect(bar_x, int(bar_y), bar_w, int(bar_h))

        # Labels
        painter.setPen(QColor(220, 220, 220))
        painter.setFont(QFont("Arial", 8))
        painter.drawText(bar_x + bar_w + 3, int(bar_y) + 8, f"{self.vmax:.1f}")
        painter.drawText(bar_x + bar_w + 3, int(bar_y + bar_h/2) + 3, f"{(self.vmin+self.vmax)/2:.1f}")
        painter.drawText(bar_x + bar_w + 3, int(bar_y + bar_h) + 3, f"{self.vmin:.1f}")
        painter.drawText(bar_x, h - 8, "水深 (m)")
        painter.end()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.model = GridModel()
        self.setWindowTitle("3DWET 网格编辑器")
        self.resize(1500, 950)
        self.setMinimumSize(1000, 600)

        self._build_ui()
        self._build_menus()
        self._build_toolbar()
        self._build_docks()
        self._connect_signals()
        self._update_action_states()
        self._show_welcome()

    # ── UI Construction ──────────────────────────────────────────────────

    def _build_ui(self):
        central = QWidget()
        layout = QHBoxLayout(central)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)

        self.grid_view = GridView(self.model)
        self.grid_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.grid_view, stretch=1)

        self.color_bar = ColorBarWidget()
        layout.addWidget(self.color_bar)

        self.setCentralWidget(central)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("就绪")
        self.status_label.setMinimumWidth(300)
        self.status_bar.addWidget(self.status_label, stretch=1)

        self.cell_info_label = QLabel("悬停网格查看信息")
        self.cell_info_label.setMinimumWidth(250)
        self.status_bar.addPermanentWidget(self.cell_info_label)

        self.zoom_label = QLabel("缩放: 100%")
        self.zoom_label.setMinimumWidth(100)
        self.status_bar.addPermanentWidget(self.zoom_label)

        self.tool_label = QLabel("工具: 平移")
        self.tool_label.setMinimumWidth(120)
        self.status_bar.addPermanentWidget(self.tool_label)

    def _build_menus(self):
        menubar = self.menuBar()

        # File
        file_menu = menubar.addMenu("文件(&F)")

        self.action_new = QAction("新建网格...", self)
        self.action_new.setShortcut(QKeySequence.New)
        self.action_new.setShortcutVisibleInContextMenu(True)
        self.action_new.triggered.connect(self.new_grid)
        file_menu.addAction(self.action_new)

        self.action_open = QAction("打开 bathymetry...", self)
        self.action_open.setShortcut(QKeySequence.Open)
        self.action_open.triggered.connect(self.open_bathymetry)
        file_menu.addAction(self.action_open)

        self.action_open_rivers = QAction("打开河流文件...", self)
        self.action_open_rivers.setShortcut("Ctrl+Shift+O")
        self.action_open_rivers.triggered.connect(self.open_rivers)
        file_menu.addAction(self.action_open_rivers)

        file_menu.addSeparator()

        self.action_save = QAction("保存 bathymetry", self)
        self.action_save.setShortcut(QKeySequence.Save)
        self.action_save.triggered.connect(self.save_bathymetry)
        file_menu.addAction(self.action_save)

        self.action_save_as = QAction("另存为...", self)
        self.action_save_as.setShortcut(QKeySequence.SaveAs)
        self.action_save_as.triggered.connect(self.save_bathymetry_as)
        file_menu.addAction(self.action_save_as)

        self.action_save_rivers = QAction("保存河流文件", self)
        self.action_save_rivers.setShortcut("Ctrl+Shift+S")
        self.action_save_rivers.triggered.connect(self.save_rivers)
        file_menu.addAction(self.action_save_rivers)

        file_menu.addSeparator()
        action_exit = QAction("退出", self)
        action_exit.triggered.connect(self.close)
        file_menu.addAction(action_exit)

        # Edit
        edit_menu = menubar.addMenu("编辑(&E)")
        self.action_undo = QAction("撤销", self)
        self.action_undo.setShortcut(QKeySequence.Undo)
        self.action_undo.triggered.connect(self.undo)
        edit_menu.addAction(self.action_undo)

        self.action_redo = QAction("重做", self)
        self.action_redo.setShortcut(QKeySequence.Redo)
        self.action_redo.triggered.connect(self.redo)
        edit_menu.addAction(self.action_redo)

        edit_menu.addSeparator()
        self.action_smooth_all = QAction("全湖平滑", self)
        self.action_smooth_all.triggered.connect(self.smooth_all_water)
        edit_menu.addAction(self.action_smooth_all)

        # View
        view_menu = menubar.addMenu("视图(&V)")
        action_fit = QAction("适应窗口", self)
        action_fit.setShortcut("R")
        action_fit.triggered.connect(self.grid_view.fit_to_view)
        view_menu.addAction(action_fit)

        action_zoom_in = QAction("放大", self)
        action_zoom_in.setShortcut("Ctrl++")
        action_zoom_in.triggered.connect(lambda: self.grid_view.scale(1.2, 1.2))
        view_menu.addAction(action_zoom_in)

        action_zoom_out = QAction("缩小", self)
        action_zoom_out.setShortcut("Ctrl+-")
        action_zoom_out.triggered.connect(lambda: self.grid_view.scale(1/1.2, 1/1.2))
        view_menu.addAction(action_zoom_out)

        view_menu.addSeparator()
        self.action_show_rivers = QAction("显示河流标记", self, checkable=True)
        self.action_show_rivers.setChecked(True)
        self.action_show_rivers.triggered.connect(self.toggle_rivers)
        view_menu.addAction(self.action_show_rivers)

        self.action_show_grid = QAction("显示网格线", self, checkable=True)
        self.action_show_grid.setChecked(True)
        self.action_show_grid.triggered.connect(self.toggle_grid_lines)
        view_menu.addAction(self.action_show_grid)

        # Tools
        tools_menu = menubar.addMenu("工具(&T)")
        self.tool_actions = {}
        tool_defs = [
            (TOOL_PAN, "平移", "1", "平移视图（也可按住鼠标左键/中键拖动）"),
            (TOOL_PAINT, "绘制水深", "2", "点击/拖动设置水深，[ / ] 调节笔刷大小"),
            (TOOL_TOGGLE, "切换水域/陆地", "3", "点击切换单元格类型"),
            (TOOL_SMOOTH, "平滑", "4", "3x3 邻域平均平滑"),
            (TOOL_RIVER, "添加河流", "5", "点击水域格添加河流入/出流点"),
            (TOOL_INFO, "信息", "6", "查看单元格详细信息"),
        ]
        tool_group = QActionGroup(self)
        tool_group.setExclusive(True)
        for tool_id, name, shortcut, tip in tool_defs:
            action = QAction(name, self, checkable=True)
            action.setShortcut(shortcut)
            action.setToolTip(f"{name} (快捷键: {shortcut})\n{tip}")
            action.setStatusTip(tip)
            action.triggered.connect(lambda checked, t=tool_id: self._set_tool(t))
            tool_group.addAction(action)
            tools_menu.addAction(action)
            self.tool_actions[tool_id] = action
        self.tool_actions[TOOL_PAN].setChecked(True)

        # Help
        help_menu = menubar.addMenu("帮助(&H)")
        action_help = QAction("使用说明", self)
        action_help.setShortcut("F1")
        action_help.triggered.connect(self.show_help)
        help_menu.addAction(action_help)

        action_about = QAction("关于", self)
        action_about.triggered.connect(self.show_about)
        help_menu.addAction(action_about)

    def _build_toolbar(self):
        toolbar = QToolBar("主工具栏")
        toolbar.setIconSize(QSize(28, 28))
        toolbar.setMovable(False)
        toolbar.setStyleSheet("""
            QToolBar { spacing: 4px; padding: 4px; background: #2d2d32; }
            QToolBar QToolButton {
                background: #3a3a42; color: #e0e0e0; border: 1px solid #555;
                border-radius: 4px; padding: 4px 10px; font-size: 12px;
                min-width: 60px;
            }
            QToolBar QToolButton:hover { background: #4a4a55; }
            QToolBar QToolButton:checked { background: #5a7a9a; border-color: #7ab0e0; }
            QToolBar QLabel { color: #ccc; font-size: 12px; padding: 0 4px; }
            QToolBar QSpinBox, QToolBar QDoubleSpinBox {
                background: #3a3a42; color: #e0e0e0; border: 1px solid #555;
                border-radius: 3px; padding: 2px;
            }
        """)
        self.addToolBar(toolbar)

        # File actions
        toolbar.addAction(self.action_new)
        toolbar.addAction(self.action_open)
        toolbar.addAction(self.action_save)
        toolbar.addSeparator()

        # Undo/redo
        toolbar.addAction(self.action_undo)
        toolbar.addAction(self.action_redo)
        toolbar.addSeparator()

        # Tool buttons
        for tool_id, action in self.tool_actions.items():
            toolbar.addAction(action)

        toolbar.addSeparator()

        # Brush size
        toolbar.addWidget(QLabel(" 笔刷:"))
        self.brush_spin = QSpinBox()
        self.brush_spin.setRange(1, 20)
        self.brush_spin.setValue(1)
        self.brush_spin.setFixedWidth(55)
        self.brush_spin.setToolTip("笔刷大小（[ 减小，] 增大）")
        self.brush_spin.valueChanged.connect(self._set_brush_size)
        toolbar.addWidget(self.brush_spin)

        # Paint depth
        toolbar.addWidget(QLabel(" 水深:"))
        self.depth_spin = QDoubleSpinBox()
        self.depth_spin.setRange(0.1, 100.0)
        self.depth_spin.setValue(3.0)
        self.depth_spin.setSingleStep(0.5)
        self.depth_spin.setSuffix(" m")
        self.depth_spin.setFixedWidth(85)
        self.depth_spin.setToolTip("绘制工具使用的水深值")
        toolbar.addWidget(self.depth_spin)

        toolbar.addSeparator()
        action_fit = QAction("适应", self)
        action_fit.setShortcut("R")
        action_fit.setToolTip("适应窗口 (R)")
        action_fit.triggered.connect(self.grid_view.fit_to_view)
        toolbar.addAction(action_fit)

    def _build_docks(self):
        # ── Tool Options Dock ──
        tool_dock = QDockWidget("工具选项", self)
        tool_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        tool_dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        tool_widget = QWidget()
        tool_layout = QVBoxLayout(tool_widget)
        tool_layout.setContentsMargins(8, 8, 8, 8)

        # Paint options
        paint_group = QGroupBox("绘制工具")
        paint_form = QFormLayout()
        self.paint_depth_spin = QDoubleSpinBox()
        self.paint_depth_spin.setRange(0.1, 100.0)
        self.paint_depth_spin.setValue(3.0)
        self.paint_depth_spin.setSingleStep(0.5)
        self.paint_depth_spin.setSuffix(" m")
        paint_form.addRow("水深:", self.paint_depth_spin)
        self.brush_size_spin = QSpinBox()
        self.brush_size_spin.setRange(1, 20)
        self.brush_size_spin.setValue(1)
        paint_form.addRow("笔刷大小:", self.brush_size_spin)
        paint_group.setLayout(paint_form)
        tool_layout.addWidget(paint_group)

        # River options
        river_group = QGroupBox("河流工具")
        river_form = QFormLayout()
        self.river_name_edit = QComboBox()
        self.river_name_edit.setEditable(True)
        self.river_name_edit.addItems(["INFL_NW", "INFL_NE", "INFL_W", "OUTFL_S", "OUTFL_E", "INFL_1", "OUTFL_1"])
        river_form.addRow("河流名称:", self.river_name_edit)
        river_hint = QLabel("提示: 名称以 OUT 开头视为出流，其他为入流")
        river_hint.setStyleSheet("color: #888; font-size: 10px;")
        river_hint.setWordWrap(True)
        river_form.addRow("", river_hint)
        river_group.setLayout(river_form)
        tool_layout.addWidget(river_group)

        # Smooth options
        smooth_group = QGroupBox("平滑工具")
        smooth_form = QFormLayout()
        self.smooth_iter_spin = QSpinBox()
        self.smooth_iter_spin.setRange(1, 20)
        self.smooth_iter_spin.setValue(1)
        smooth_form.addRow("迭代次数:", self.smooth_iter_spin)
        btn_smooth_all = QPushButton("对全部水域平滑")
        btn_smooth_all.clicked.connect(self.smooth_all_water)
        smooth_form.addRow("", btn_smooth_all)
        smooth_group.setLayout(smooth_form)
        tool_layout.addWidget(smooth_group)

        tool_layout.addStretch()
        tool_dock.setWidget(tool_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, tool_dock)

        # Sync controls
        self.paint_depth_spin.valueChanged.connect(self.depth_spin.setValue)
        self.depth_spin.valueChanged.connect(self.paint_depth_spin.setValue)
        self.brush_size_spin.valueChanged.connect(self.brush_spin.setValue)
        self.brush_spin.valueChanged.connect(self.brush_size_spin.setValue)

        # ── Grid Info Dock ──
        info_dock = QDockWidget("网格信息", self)
        info_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        info_dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        info_widget = QWidget()
        info_layout = QFormLayout(info_widget)
        info_layout.setContentsMargins(8, 8, 8, 8)
        self.info_nx = QLabel("-")
        self.info_water = QLabel("-")
        self.info_land = QLabel("-")
        self.info_dmin = QLabel("-")
        self.info_dmax = QLabel("-")
        self.info_dmean = QLabel("-")
        self.info_dx = QLabel("-")
        self.info_rivers = QLabel("-")
        info_layout.addRow("网格尺寸:", self.info_nx)
        info_layout.addRow("水域格数:", self.info_water)
        info_layout.addRow("陆地格数:", self.info_land)
        info_layout.addRow("最小水深:", self.info_dmin)
        info_layout.addRow("最大水深:", self.info_dmax)
        info_layout.addRow("平均水深:", self.info_dmean)
        info_layout.addRow("格网分辨率:", self.info_dx)
        info_layout.addRow("河流数量:", self.info_rivers)
        info_dock.setWidget(info_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, info_dock)

        # ── River List Dock ──
        river_dock = QDockWidget("河流列表", self)
        river_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        river_dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        river_widget = QWidget()
        river_layout = QVBoxLayout(river_widget)
        river_layout.setContentsMargins(8, 8, 8, 8)
        self.river_list = QListWidget()
        self.river_list.setSelectionMode(QListWidget.SingleSelection)
        river_layout.addWidget(self.river_list)
        btn_layout = QHBoxLayout()
        btn_remove_river = QPushButton("删除选中")
        btn_remove_river.clicked.connect(self._remove_selected_river)
        btn_layout.addWidget(btn_remove_river)
        btn_refresh = QPushButton("刷新")
        btn_refresh.clicked.connect(self._update_river_list)
        btn_layout.addWidget(btn_refresh)
        river_layout.addLayout(btn_layout)
        river_dock.setWidget(river_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, river_dock)

        # Tabify right docks
        self.tabifyDockWidget(info_dock, river_dock)
        info_dock.raise_()

    def _connect_signals(self):
        self.grid_view.cell_clicked.connect(self._on_cell_clicked)
        self.grid_view.cell_dragged.connect(self._on_cell_dragged)
        self.grid_view.cell_hovered.connect(self._on_cell_hovered)
        self.grid_view.cell_left.connect(self._on_cell_left)
        self.grid_view.view_changed.connect(self._update_zoom_label)
        self.grid_view.tool_changed.connect(self._on_tool_changed)

    # ── Welcome / Help ───────────────────────────────────────────────────

    def _show_welcome(self):
        QTimer.singleShot(300, self._welcome_message)

    def _welcome_message(self):
        self.status_label.setText("欢迎使用 3DWET 网格编辑器 | 按 F1 查看使用说明 | 快捷键: 1-6 切换工具, R 适应窗口")

    def show_help(self):
        help_text = """
<h3>3DWET 网格编辑器 使用说明</h3>
<table border="0" cellpadding="4">
<tr><td><b>文件操作</b></td><td></td></tr>
<tr><td>Ctrl+N</td><td>新建空白网格</td></tr>
<tr><td>Ctrl+O</td><td>打开 bathymetry.nc</td></tr>
<tr><td>Ctrl+S</td><td>保存 bathymetry.nc</td></tr>
<tr><td>Ctrl+Shift+S</td><td>保存河流文件</td></tr>
<tr><td><b>工具切换</b></td><td></td></tr>
<tr><td>1</td><td>平移工具 - 拖动平移视图</td></tr>
<tr><td>2</td><td>绘制水深 - 点击/拖动设置水深</td></tr>
<tr><td>3</td><td>切换水域/陆地</td></tr>
<tr><td>4</td><td>平滑工具 - 3x3 邻域平均</td></tr>
<tr><td>5</td><td>添加河流 - 点击水域格添加</td></tr>
<tr><td>6</td><td>信息工具 - 查看单元格详情</td></tr>
<tr><td><b>视图操作</b></td><td></td></tr>
<tr><td>滚轮</td><td>缩放</td></tr>
<tr><td>R</td><td>适应窗口</td></tr>
<tr><td>Ctrl++ / Ctrl+-</td><td>放大/缩小</td></tr>
<tr><td>中键拖动 / 左键拖动(平移工具)</td><td>平移视图</td></tr>
<tr><td><b>编辑操作</b></td><td></td></tr>
<tr><td>[ / ]</td><td>减小/增大笔刷</td></tr>
<tr><td>Ctrl+Z / Ctrl+Y</td><td>撤销/重做</td></tr>
<tr><td>右键</td><td>上下文菜单（快速操作）</td></tr>
<tr><td>Esc</td><td>切回平移工具，取消选中</td></tr>
</table>
<p><b>颜色说明:</b> 棕色=陆地，蓝绿色系=水域（越深越偏蓝），蓝色方块=入流河流，橙色方块=出流河流，黄色虚线=当前笔刷范围</p>
"""
        QMessageBox.information(self, "使用说明", help_text)

    def show_about(self):
        QMessageBox.about(self, "关于",
            "<h3>3DWET 网格编辑器</h3>"
            "<p>基于 GETM-FABM-WET 的三维水动力-水质-食物网耦合模型前处理工具</p>"
            "<p>支持 bathymetry.nc 网格编辑和 riverinfo.dat 河流配置</p>"
            "<p>技术栈: Python + PyQt5 + netCDF4 + numpy</p>")

    # ── File Operations ──────────────────────────────────────────────────

    def new_grid(self):
        if self.model.modified:
            reply = QMessageBox.question(self, "未保存的更改",
                "当前网格有未保存的更改，是否继续？",
                QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.No:
                return
        dlg = NewGridDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            p = dlg.get_params()
            self.model.nx = p['nx']
            self.model.ny = p['ny']
            self.model.cell_dx = p['dx']
            self.model.cell_dy = p['dy']
            self.model.bathymetry = np.full((p['ny'], p['nx']),
                p['depth'] if p['depth'] > 0 else LAND_VALUE, dtype=np.float64)
            self.model.x_coords = np.arange(p['nx']) * p['dx'] + p['dx']/2
            self.model.y_coords = np.arange(p['ny']) * p['dy'] + p['dy']/2
            self.model.lonc = np.zeros((p['ny'], p['nx']))
            self.model.latc = np.zeros((p['ny'], p['nx']))
            self.model.rivers = []
            self.model.filepath = None
            self.model.river_filepath = None
            self.model.modified = True
            self.model._undo_stack.clear()
            self.model._redo_stack.clear()
            self.grid_view.rebuild()
            self._update_info_panel()
            self._update_river_list()
            self._update_colorbar()
            self._update_action_states()
            self.setWindowTitle("3DWET 网格编辑器 - 未命名")
            self.status_label.setText(f"已新建 {p['nx']}x{p['ny']} 网格")

    def open_bathymetry(self):
        if self.model.modified:
            reply = QMessageBox.question(self, "未保存的更改",
                "当前网格有未保存的更改，是否继续？",
                QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.No:
                return
        path, _ = QFileDialog.getOpenFileName(
            self, "打开 bathymetry", "", "NetCDF 文件 (*.nc);;所有文件 (*.*)"
        )
        if path:
            try:
                self.model.load_bathymetry(path)
                river_path = Path(path).parent / "riverinfo.dat"
                if river_path.exists():
                    self.model.load_rivers(str(river_path))
                self.grid_view.rebuild()
                self._update_info_panel()
                self._update_river_list()
                self._update_colorbar()
                self._update_action_states()
                self.setWindowTitle(f"3DWET 网格编辑器 - {Path(path).name}")
                self.status_label.setText(f"已加载: {Path(path).name}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"加载失败:\n{e}")

    def open_rivers(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "打开 riverinfo.dat", "", "数据文件 (*.dat *.txt);;所有文件 (*.*)"
        )
        if path:
            try:
                self.model.load_rivers(path)
                self.grid_view.refresh_rivers()
                self._update_river_list()
                self._update_info_panel()
                self.status_label.setText(f"已加载河流: {Path(path).name}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"加载河流失败:\n{e}")

    def save_bathymetry(self):
        if self.model.filepath is None:
            self.save_bathymetry_as()
            return
        try:
            self.model.save_bathymetry()
            self.status_label.setText(f"已保存: {self.model.filepath.name}")
            self._flash_status("保存成功", 2000)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败:\n{e}")

    def save_bathymetry_as(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "另存为", "bathymetry.nc", "NetCDF 文件 (*.nc)"
        )
        if path:
            try:
                self.model.save_bathymetry(path)
                self.setWindowTitle(f"3DWET 网格编辑器 - {Path(path).name}")
                self.status_label.setText(f"已保存: {Path(path).name}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存失败:\n{e}")

    def save_rivers(self):
        if self.model.river_filepath is None:
            path, _ = QFileDialog.getSaveFileName(
                self, "保存河流文件", "riverinfo.dat", "数据文件 (*.dat)"
            )
            if not path:
                return
        else:
            path = str(self.model.river_filepath)
        try:
            self.model.save_rivers(path)
            self.status_label.setText(f"已保存河流: {Path(path).name}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存河流失败:\n{e}")

    def _flash_status(self, msg, duration=2000):
        self.status_label.setText(msg)
        QTimer.singleShot(duration, lambda: self._update_status())

    # ── Edit Operations ──────────────────────────────────────────────────

    def undo(self):
        if self.model.undo():
            self.grid_view.refresh_cells()
            self.grid_view.refresh_rivers()
            self._update_info_panel()
            self._update_river_list()
            self._update_action_states()
            self.status_label.setText("已撤销")

    def redo(self):
        if self.model.redo():
            self.grid_view.refresh_cells()
            self.grid_view.refresh_rivers()
            self._update_info_panel()
            self._update_river_list()
            self._update_action_states()
            self.status_label.setText("已重做")

    def smooth_all_water(self):
        water_cells = list(zip(*np.where(self.model.bathymetry > 0)))
        water_cells = [(j, i) for i, j in water_cells]  # convert to (i,j)
        if not water_cells:
            return
        iters = self.smooth_iter_spin.value()
        for _ in range(iters):
            self.model.smooth_region(water_cells, record_undo=False)
        self.model._push_undo()
        self.grid_view.refresh_cells()
        self._update_info_panel()
        self._update_action_states()
        self.status_label.setText(f"已对 {len(water_cells)} 个水域格执行 {iters} 次平滑")

    # ── Tool Handlers ────────────────────────────────────────────────────

    def _set_tool(self, tool):
        self.grid_view.set_tool(tool)
        for tid, action in self.tool_actions.items():
            action.setChecked(tid == tool)

    def _on_tool_changed(self, tool):
        names = {TOOL_PAN: "平移", TOOL_PAINT: "绘制水深", TOOL_TOGGLE: "切换水域/陆地",
                 TOOL_SMOOTH: "平滑", TOOL_RIVER: "添加河流", TOOL_INFO: "信息"}
        self.tool_label.setText(f"工具: {names.get(tool, '?')}")
        for tid, action in self.tool_actions.items():
            action.setChecked(tid == tool)

    def _set_brush_size(self, size):
        self.grid_view.brush_size = size

    def _on_cell_clicked(self, i, j, event):
        tool = self.grid_view.tool
        if tool == TOOL_PAINT:
            depth = self.depth_spin.value()
            cells = self.grid_view.get_brush_cells(i, j)
            self.model.paint_region(cells, depth)
            self.grid_view.refresh_cells(cells)
        elif tool == TOOL_TOGGLE:
            cells = self.grid_view.get_brush_cells(i, j)
            self.model._push_undo()
            for ci, cj in cells:
                self.model.toggle_land(ci, cj, record_undo=False)
            self.grid_view.refresh_cells(cells)
        elif tool == TOOL_SMOOTH:
            cells = self.grid_view.get_brush_cells(i, j)
            self.model.smooth_region(cells)
            self.grid_view.refresh_cells(cells)
        elif tool == TOOL_RIVER:
            if not self.model.is_water(i, j):
                self.status_label.setText("警告: 河流只能添加在水域格上")
                return
            name = self.river_name_edit.currentText().strip()
            if name:
                self.model.add_river(i, j, name)
                self.grid_view.refresh_rivers()
                self._update_river_list()
        elif tool == TOOL_INFO:
            pass

        self._update_info_panel()
        self._update_action_states()
        self._update_status()

    def _on_cell_dragged(self, i, j):
        tool = self.grid_view.tool
        if tool == TOOL_PAINT:
            depth = self.depth_spin.value()
            cells = self.grid_view.get_brush_cells(i, j)
            self.model.paint_region(cells, depth, record_undo=False)
            self.grid_view.refresh_cells(cells)
        elif tool == TOOL_TOGGLE:
            cells = self.grid_view.get_brush_cells(i, j)
            for ci, cj in cells:
                self.model.toggle_land(ci, cj, record_undo=False)
            self.grid_view.refresh_cells(cells)
        elif tool == TOOL_SMOOTH:
            cells = self.grid_view.get_brush_cells(i, j)
            self.model.smooth_region(cells, record_undo=False)
            self.grid_view.refresh_cells(cells)

    def _on_cell_hovered(self, i, j):
        depth = self.model.get_depth(i, j)
        is_water = self.model.is_water(i, j)
        typ = "水域" if is_water else "陆地"
        self.cell_info_label.setText(f"({i+1},{j+1}) {typ} {depth:.2f}m")

    def _on_cell_left(self):
        self.cell_info_label.setText("悬停网格查看信息")

    def _update_zoom_label(self):
        zoom = self.grid_view.get_zoom_level()
        self.zoom_label.setText(f"缩放: {zoom*100:.0f}%")

    def _update_status(self):
        if self.model.nx > 0:
            self.status_label.setText(
                f"{self.model.nx}×{self.model.ny} | "
                f"{self.model.water_count()} 水域 | "
                f"{self.model.nx*self.model.ny - self.model.water_count()} 陆地"
            )

    def _update_action_states(self):
        self.action_undo.setEnabled(self.model.can_undo())
        self.action_redo.setEnabled(self.model.can_redo())
        has_grid = self.model.nx > 0
        self.action_save.setEnabled(has_grid)
        self.action_save_as.setEnabled(has_grid)
        self.action_save_rivers.setEnabled(has_grid and len(self.model.rivers) > 0)
        self.action_smooth_all.setEnabled(has_grid and self.model.water_count() > 0)

    def _update_info_panel(self):
        if self.model.nx == 0:
            return
        self.info_nx.setText(f"{self.model.nx} × {self.model.ny}")
        self.info_water.setText(str(self.model.water_count()))
        self.info_land.setText(str(self.model.nx * self.model.ny - self.model.water_count()))
        dmin, dmax = self.model.depth_range()
        self.info_dmin.setText(f"{dmin:.2f} m")
        self.info_dmax.setText(f"{dmax:.2f} m")
        water = self.model.bathymetry[self.model.bathymetry > 0]
        self.info_dmean.setText(f"{np.mean(water):.2f} m" if len(water) > 0 else "-")
        self.info_dx.setText(f"{self.model.cell_dx:.0f} × {self.model.cell_dy:.0f} m")
        self.info_rivers.setText(str(len(self.model.rivers)))
        self._update_colorbar()

    def _update_colorbar(self):
        dmin, dmax = self.model.depth_range()
        if dmax > 0:
            self.color_bar.set_range(0, max(dmax, 1.0), self.grid_view.cmap)

    def _update_river_list(self):
        self.river_list.clear()
        groups = self.model.get_river_groups()
        for name, cells in groups.items():
            is_inflow = not name.upper().startswith('OUT')
            direction = "入流" if is_inflow else "出流"
            coords = ", ".join([f"({i+1},{j+1})" for i, j in cells])
            item = QListWidgetItem(f"[{direction}] {name} ({len(cells)}格) {coords}")
            item.setData(Qt.UserRole, name)
            self.river_list.addItem(item)

    def _remove_selected_river(self):
        item = self.river_list.currentItem()
        if item is None:
            return
        name = item.data(Qt.UserRole)
        to_remove = [idx for idx, r in enumerate(self.model.rivers) if r.name == name]
        if to_remove:
            reply = QMessageBox.question(self, "确认删除",
                f"确定删除河流 '{name}'（{len(to_remove)} 个格点）？",
                QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.model._push_undo()
                for idx in reversed(to_remove):
                    self.model.rivers.pop(idx)
                self.model.modified = True
                self.grid_view.refresh_rivers()
                self._update_river_list()
                self._update_info_panel()
                self._update_action_states()

    def toggle_rivers(self, show):
        for item in self.grid_view.river_items:
            item.setVisible(show)

    def toggle_grid_lines(self, show):
        for item in self.grid_view.cell_items.values():
            if show:
                item.setPen(QPen(QColor(60, 60, 65), 0.5))
            else:
                item.setPen(QPen(Qt.NoPen))

    # ── Close ────────────────────────────────────────────────────────────

    def closeEvent(self, event):
        if self.model.modified:
            reply = QMessageBox.question(
                self, "未保存的更改",
                "有未保存的更改，是否保存？",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            if reply == QMessageBox.Save:
                self.save_bathymetry()
                if self.model.modified:
                    event.ignore()
                    return
            elif reply == QMessageBox.Cancel:
                event.ignore()
                return
        event.accept()
