"""
3DWET 网格编辑器 - 入口
启动方式: python main.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor

from main_window import MainWindow


def apply_dark_theme(app):
    """Apply a clean dark theme."""
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(45, 45, 50))
    palette.setColor(QPalette.WindowText, QColor(220, 220, 220))
    palette.setColor(QPalette.Base, QColor(35, 35, 40))
    palette.setColor(QPalette.AlternateBase, QColor(50, 50, 55))
    palette.setColor(QPalette.ToolTipBase, QColor(60, 60, 70))
    palette.setColor(QPalette.ToolTipText, QColor(230, 230, 230))
    palette.setColor(QPalette.Text, QColor(220, 220, 220))
    palette.setColor(QPalette.Button, QColor(55, 55, 62))
    palette.setColor(QPalette.ButtonText, QColor(220, 220, 220))
    palette.setColor(QPalette.BrightText, QColor(255, 100, 100))
    palette.setColor(QPalette.Link, QColor(80, 150, 220))
    palette.setColor(QPalette.Highlight, QColor(70, 120, 180))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)

    app.setStyleSheet("""
        QToolTip {
            background-color: #3c3c45; color: #e8e8e8;
            border: 1px solid #666; padding: 4px; font-size: 12px;
        }
        QDockWidget { title: close; font-size: 12px; }
        QDockWidget::title {
            background: #35353c; padding: 6px 8px; color: #ddd;
        }
        QGroupBox {
            border: 1px solid #555; border-radius: 4px;
            margin-top: 10px; padding-top: 8px; font-size: 12px; color: #ccc;
        }
        QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 4px; }
        QListWidget { background: #2a2a30; border: 1px solid #444; }
        QListWidget::item { padding: 3px; }
        QListWidget::item:selected { background: #4a6a8a; }
        QMenu { background: #35353c; color: #ddd; border: 1px solid #555; }
        QMenu::item:selected { background: #4a6a8a; }
        QMenu::item:disabled { color: #777; }
        QSpinBox, QDoubleSpinBox, QComboBox, QLineEdit {
            background: #2a2a30; color: #ddd; border: 1px solid #555;
            border-radius: 3px; padding: 2px 4px;
        }
        QPushButton {
            background: #3a3a44; color: #ddd; border: 1px solid #555;
            border-radius: 4px; padding: 5px 12px;
        }
        QPushButton:hover { background: #4a4a58; }
        QPushButton:pressed { background: #3570a0; }
        QLabel { color: #ccc; }
        QStatusBar { background: #2a2a30; color: #aaa; }
        QMenuBar { background: #2d2d32; color: #ddd; }
        QMenuBar::item:selected { background: #4a4a55; }
    """)


def main():
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("3DWET Grid Editor")
    app.setOrganizationName("3DWET")

    apply_dark_theme(app)

    font = QFont("Microsoft YaHei", 9)
    app.setFont(font)

    window = MainWindow()
    window.show()

    # Auto-load theoretical lake if available
    default_bathy = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "case", "Theoretical lake", "bathymetry.nc"
    )
    if os.path.exists(default_bathy):
        try:
            window.model.load_bathymetry(default_bathy)
            river_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "case", "Theoretical lake", "riverinfo.dat"
            )
            if os.path.exists(river_path):
                window.model.load_rivers(river_path)
            window.grid_view.rebuild()
            window._update_info_panel()
            window._update_river_list()
            window._update_colorbar()
            window._update_action_states()
            window.setWindowTitle("3DWET 网格编辑器 - 理论湖 (默认加载)")
            window.status_label.setText("已自动加载理论湖案例 | 按 F1 查看使用说明")
        except Exception as e:
            window.status_label.setText(f"自动加载失败: {e}")

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
