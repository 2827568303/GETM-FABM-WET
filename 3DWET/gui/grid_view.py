"""
3DWET Grid Editor - Grid View Widget
QGraphicsView-based canvas for rendering and interacting with the Cartesian grid.
"""
import numpy as np
from PyQt5.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsSimpleTextItem,
    QToolTip, QMenu, QAction, QApplication, QGraphicsLineItem
)
from PyQt5.QtCore import Qt, QRectF, QPointF, pyqtSignal, QSize, QPoint
from PyQt5.QtGui import (
    QColor, QPainter, QPen, QBrush, QFont, QMouseEvent, QWheelEvent,
    QKeyEvent, QTransform, QPolygonF, QPainterPath, QCursor
)
from matplotlib import cm
from matplotlib.colors import Normalize

from grid_model import GridModel, LAND_VALUE


# Tool IDs
TOOL_PAN = 0
TOOL_PAINT = 1
TOOL_TOGGLE = 2
TOOL_SMOOTH = 3
TOOL_RIVER = 4
TOOL_INFO = 5
TOOL_FILL = 6  # flood fill region


class GridCellItem(QGraphicsRectItem):
    """A single grid cell. Stores its (i, j) 0-based indices."""
    def __init__(self, i: int, j: int, x: float, y: float, w: float, h: float):
        super().__init__(x, y, w, h)
        self.i = i
        self.j = j
        self.setAcceptHoverEvents(True)
        self._selected = False

    def set_selected(self, sel: bool):
        self._selected = sel
        if sel:
            self.setPen(QPen(QColor(255, 255, 0), 2))
        else:
            self.setPen(QPen(QColor(60, 60, 65), 0.5))

    def hoverEnterEvent(self, event):
        view = self.scene().views()[0] if self.scene() else None
        if view:
            view.cell_hovered.emit(self.i, self.j)
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        view = self.scene().views()[0] if self.scene() else None
        if view:
            view.cell_left.emit()
        super().hoverLeaveEvent(event)


class RiverMarkerItem(QGraphicsRectItem):
    """Marker for a river cell with label."""
    def __init__(self, i: int, j: int, x: float, y: float, w: float, h: float,
                 name: str, is_inflow: bool, show_label: bool = True):
        super().__init__(x + w * 0.12, y + h * 0.12, w * 0.76, h * 0.76)
        self.i = i
        self.j = j
        self.name = name
        self.is_inflow = is_inflow
        color = QColor(0, 170, 255, 220) if is_inflow else QColor(255, 130, 0, 220)
        self.setBrush(QBrush(color))
        self.setPen(QPen(Qt.white, 1.5))
        self.setZValue(10)
        self.setToolTip(f"河流: {name}  位置: ({i+1}, {j+1})  {'入流' if is_inflow else '出流'}")

        # Add direction arrow / label
        if show_label and w > 30:
            self.label = QGraphicsSimpleTextItem(name, self)
            font = QFont("Arial", 7, QFont.Bold)
            self.label.setFont(font)
            self.label.setBrush(QBrush(Qt.white))
            # Center label
            br = self.label.boundingRect()
            self.label.setPos(x + w/2 - br.width()/2, y + h/2 - br.height()/2)
            self.label.setZValue(11)


class BrushPreviewItem(QGraphicsRectItem):
    """Semi-transparent rectangle showing brush area."""
    def __init__(self):
        super().__init__(0, 0, 0, 0)
        self.setBrush(QBrush(QColor(255, 255, 0, 40)))
        self.setPen(QPen(QColor(255, 255, 0, 180), 1.5, Qt.DashLine))
        self.setZValue(20)
        self.hide()


class GridView(QGraphicsView):
    """Interactive grid canvas."""

    cell_hovered = pyqtSignal(int, int)
    cell_left = pyqtSignal()
    cell_clicked = pyqtSignal(int, int, object)
    cell_dragged = pyqtSignal(int, int)
    view_changed = pyqtSignal()
    tool_changed = pyqtSignal(int)

    def __init__(self, model: GridModel, parent=None):
        super().__init__(parent)
        self.model = model
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing, True)
        self.setRenderHint(QPainter.SmoothPixmapTransform, False)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.NoDrag)
        self.setMouseTracking(True)
        self.setBackgroundBrush(QBrush(QColor(45, 45, 50)))
        self.setFrameShape(QGraphicsView.NoFrame)

        self.tool = TOOL_PAN
        self.brush_size = 1
        self.paint_depth = 3.0
        self.cmap = cm.get_cmap('terrain')
        self.norm = Normalize(vmin=0, vmax=10)
        self.cell_items = {}
        self.river_items = []
        self.selected_cell = None
        self._is_panning = False
        self._pan_start = QPointF()
        self._last_cell = (-1, -1)
        self._drag_active = False
        self._drag_started = False

        # Brush preview
        self.brush_preview = BrushPreviewItem()
        self.scene.addItem(self.brush_preview)

        self.zoom_in_factor = 1.15
        self.zoom_out_factor = 1 / 1.15

    # ── Rendering ────────────────────────────────────────────────────────

    def rebuild(self):
        """Rebuild all cell items from the model."""
        # Remove brush preview before clearing (scene.clear would delete its C++ object)
        if self.brush_preview.scene() is not None:
            self.scene.removeItem(self.brush_preview)
        self.scene.clear()
        self.cell_items.clear()
        self.river_items.clear()
        self.selected_cell = None

        # Re-add brush preview
        self.scene.addItem(self.brush_preview)

        if self.model.nx == 0 or self.model.ny == 0:
            return

        dmin, dmax = self.model.depth_range()
        if dmax > 0:
            self.norm = Normalize(vmin=0, vmax=max(dmax, 1.0))

        w = self.model.cell_dx
        h = self.model.cell_dy

        for j in range(self.model.ny):
            for i in range(self.model.nx):
                x = i * w
                y = j * h
                item = GridCellItem(i, j, x, y, w, h)
                self._update_cell_color(item)
                self.scene.addItem(item)
                self.cell_items[(i, j)] = item

        self._rebuild_rivers()
        self.scene.setSceneRect(-w*0.5, -h*0.5, self.model.nx * w + w, self.model.ny * h + h)
        self.fit_to_view()

    def _update_cell_color(self, item: GridCellItem):
        depth = self.model.bathymetry[item.j, item.i]
        if depth <= 0:
            item.setBrush(QBrush(QColor(90, 78, 55)))
        else:
            rgba = self.cmap(self.norm(depth))
            color = QColor(int(rgba[0]*255), int(rgba[1]*255), int(rgba[2]*255), 255)
            item.setBrush(QBrush(color))

    def refresh_cells(self, cells=None):
        if cells is None:
            for item in self.cell_items.values():
                self._update_cell_color(item)
        else:
            for i, j in cells:
                if (i, j) in self.cell_items:
                    self._update_cell_color(self.cell_items[(i, j)])

    def _rebuild_rivers(self):
        for item in self.river_items:
            self.scene.removeItem(item)
        self.river_items.clear()

        w = self.model.cell_dx
        h = self.model.cell_dy
        groups = self.model.get_river_groups()
        for name, cells in groups.items():
            is_inflow = not name.upper().startswith('OUT')
            for i, j in cells:
                if 0 <= i < self.model.nx and 0 <= j < self.model.ny:
                    marker = RiverMarkerItem(i, j, i*w, j*h, w, h, name, is_inflow, show_label=(w*self.get_zoom_level() > 40))
                    self.scene.addItem(marker)
                    self.river_items.append(marker)

    def refresh_rivers(self):
        self._rebuild_rivers()

    def set_selected_cell(self, i, j):
        if self.selected_cell and self.selected_cell in self.cell_items:
            self.cell_items[self.selected_cell].set_selected(False)
        if i is not None and j is not None and (i, j) in self.cell_items:
            self.cell_items[(i, j)].set_selected(True)
            self.selected_cell = (i, j)
        else:
            self.selected_cell = None

    # ── View controls ────────────────────────────────────────────────────

    def fit_to_view(self):
        if self.model.nx > 0:
            self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
            self.view_changed.emit()

    def wheelEvent(self, event: QWheelEvent):
        if event.angleDelta().y() > 0:
            self.scale(self.zoom_in_factor, self.zoom_in_factor)
        else:
            self.scale(self.zoom_out_factor, self.zoom_out_factor)
        self.view_changed.emit()
        self._update_brush_preview(event.pos())
        # Update river label visibility based on zoom
        self._update_river_labels()

    def _update_river_labels(self):
        zoom = self.get_zoom_level()
        w = self.model.cell_dx
        visible = w * zoom > 40
        for item in self.river_items:
            if hasattr(item, 'label'):
                item.label.setVisible(visible)

    def reset_zoom(self):
        self.resetTransform()
        self.fit_to_view()
        self._update_river_labels()

    def get_zoom_level(self) -> float:
        return self.transform().m11()

    # ── Brush preview ───────────────────────────────────────────────────

    def _update_brush_preview(self, view_pos=None):
        if self.tool in (TOOL_PAN, TOOL_INFO):
            self.brush_preview.hide()
            return
        if view_pos is None:
            view_pos = self.mapFromGlobal(QCursor.pos())
        scene_pos = self.mapToScene(view_pos)
        i, j = self._scene_to_cell(scene_pos)
        if i < 0 or j < 0:
            self.brush_preview.hide()
            return
        w = self.model.cell_dx
        h = self.model.cell_dy
        r = self.brush_size
        x = (i - r + 1) * w
        y = (j - r + 1) * h
        self.brush_preview.setRect(x, y, (2*r-1)*w, (2*r-1)*h)
        self.brush_preview.show()

    # ── Mouse interaction ───────────────────────────────────────────────

    def mousePressEvent(self, event: QMouseEvent):
        scene_pos = self.mapToScene(event.pos())
        i, j = self._scene_to_cell(scene_pos)

        # Middle button = pan always
        if event.button() == Qt.MiddleButton:
            self._is_panning = True
            self._pan_start = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
            event.accept()
            return

        # Left button
        if event.button() == Qt.LeftButton:
            if self.tool == TOOL_PAN:
                self._is_panning = True
                self._pan_start = event.pos()
                self.setCursor(Qt.ClosedHandCursor)
                event.accept()
                return
            if i >= 0 and j >= 0:
                self._drag_active = True
                self._drag_started = False
                self._last_cell = (i, j)
                self.set_selected_cell(i, j)
                self.cell_clicked.emit(i, j, event)
                event.accept()
                return

        # Right button = context menu
        if event.button() == Qt.RightButton:
            self._show_context_menu(event.globalPos(), i, j)
            event.accept()
            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        # Update brush preview always
        self._update_brush_preview(event.pos())

        if self._is_panning:
            delta = event.pos() - self._pan_start
            self._pan_start = event.pos()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            event.accept()
            return

        scene_pos = self.mapToScene(event.pos())
        i, j = self._scene_to_cell(scene_pos)

        if self._drag_active and i >= 0 and j >= 0:
            if not self._drag_started or (i, j) != self._last_cell:
                self._drag_started = True
                self._last_cell = (i, j)
                self.cell_dragged.emit(i, j)

        # Hover tooltip
        if i >= 0 and j >= 0:
            depth = self.model.get_depth(i, j)
            is_water = self.model.is_water(i, j)
            rivers_here = [r.name for r in self.model.rivers if r.i-1 == i and r.j-1 == j]
            tip = f"网格 ({i+1}, {j+1})\n"
            tip += f"类型: {'水域' if is_water else '陆地'}\n"
            tip += f"水深: {depth:.2f} m"
            if rivers_here:
                tip += f"\n河流: {', '.join(set(rivers_here))}"
            QToolTip.showText(event.globalPos(), tip, self)
        else:
            QToolTip.hideText()

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self._is_panning:
            self._is_panning = False
            self._update_cursor()
            event.accept()
            return
        if self._drag_active:
            self._drag_active = False
            self._drag_started = False
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def leaveEvent(self, event):
        self.cell_left.emit()
        self.brush_preview.hide()
        QToolTip.hideText()
        super().leaveEvent(event)

    def _show_context_menu(self, global_pos, i, j):
        menu = QMenu(self)
        menu.setStyleSheet("QMenu { font-size: 12px; }")

        if i >= 0 and j >= 0:
            depth = self.model.get_depth(i, j)
            is_water = self.model.is_water(i, j)
            header = menu.addAction(f"网格 ({i+1}, {j+1})  {'水域' if is_water else '陆地'}  {depth:.2f}m")
            header.setEnabled(False)
            menu.addSeparator()

            act_paint = menu.addAction(f"设置水深为 {self.paint_depth:.1f}m")
            act_paint.triggered.connect(lambda: self.cell_clicked.emit(i, j, None))

            act_toggle = menu.addAction("切换 水域/陆地")
            act_toggle.triggered.connect(lambda: self._quick_toggle(i, j))

            act_smooth = menu.addAction("平滑此格")
            act_smooth.triggered.connect(lambda: self._quick_smooth(i, j))

            menu.addSeparator()
            act_river = menu.addAction("在此添加河流...")
            act_river.triggered.connect(lambda: self._quick_add_river(i, j))

            rivers_here = [r.name for r in self.model.rivers if r.i-1 == i and r.j-1 == j]
            if rivers_here:
                act_rm_river = menu.addAction(f"删除河流 ({', '.join(set(rivers_here))})")
                act_rm_river.triggered.connect(lambda: self.model.remove_rivers_at(i, j))

        menu.addSeparator()
        act_fit = menu.addAction("适应窗口 (R)")
        act_fit.triggered.connect(self.fit_to_view)

        menu.exec_(global_pos)

    def _quick_toggle(self, i, j):
        self.model.toggle_land(i, j)
        self.refresh_cells([(i, j)])

    def _quick_smooth(self, i, j):
        self.model.smooth_cell(i, j)
        self.refresh_cells([(i, j)])

    def _quick_add_river(self, i, j):
        from PyQt5.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "添加河流", "河流名称:", text="INFL_1")
        if ok and name.strip():
            self.model.add_river(i, j, name.strip())
            self.refresh_rivers()

    def _scene_to_cell(self, scene_pos: QPointF):
        w = self.model.cell_dx if self.model.cell_dx > 0 else 1
        h = self.model.cell_dy if self.model.cell_dy > 0 else 1
        i = int(scene_pos.x() // w)
        j = int(scene_pos.y() // h)
        if 0 <= i < self.model.nx and 0 <= j < self.model.ny:
            return i, j
        return -1, -1

    def get_brush_cells(self, center_i: int, center_j: int) -> list:
        cells = []
        r = self.brush_size
        for di in range(-r + 1, r):
            for dj in range(-r + 1, r):
                i, j = center_i + di, center_j + dj
                if 0 <= i < self.model.nx and 0 <= j < self.model.ny:
                    cells.append((i, j))
        return cells

    def set_tool(self, tool: int):
        self.tool = tool
        self._update_cursor()
        self.tool_changed.emit(tool)
        if tool in (TOOL_PAN, TOOL_INFO):
            self.brush_preview.hide()
        else:
            self._update_brush_preview()

    def _update_cursor(self):
        if self.tool == TOOL_PAN or self._is_panning:
            self.setCursor(Qt.OpenHandCursor if not self._is_panning else Qt.ClosedHandCursor)
        elif self.tool == TOOL_INFO:
            self.setCursor(Qt.WhatsThisCursor)
        else:
            self.setCursor(Qt.CrossCursor)

    # ── Keyboard ─────────────────────────────────────────────────────────

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        if key in (Qt.Key_Plus, Qt.Key_Equal, Qt.Key_BracketRight):
            self.brush_size = min(self.brush_size + 1, 20)
            self._update_brush_preview()
        elif key in (Qt.Key_Minus, Qt.Key_BracketLeft):
            self.brush_size = max(self.brush_size - 1, 1)
            self._update_brush_preview()
        elif key == Qt.Key_R:
            self.reset_zoom()
        elif key == Qt.Key_1:
            self.set_tool(TOOL_PAN)
        elif key == Qt.Key_2:
            self.set_tool(TOOL_PAINT)
        elif key == Qt.Key_3:
            self.set_tool(TOOL_TOGGLE)
        elif key == Qt.Key_4:
            self.set_tool(TOOL_SMOOTH)
        elif key == Qt.Key_5:
            self.set_tool(TOOL_RIVER)
        elif key == Qt.Key_6:
            self.set_tool(TOOL_INFO)
        elif key == Qt.Key_F:
            self.set_tool(TOOL_FILL)
        elif key == Qt.Key_Escape:
            self.set_tool(TOOL_PAN)
            self.set_selected_cell(None, None)
        else:
            super().keyPressEvent(event)
