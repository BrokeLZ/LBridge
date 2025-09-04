import hou
import sys
from functools import partial

from PySide6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QSpacerItem, QGroupBox,
    QTreeWidget, QTreeWidgetItem, QCheckBox, QComboBox, QLabel, QLineEdit,
    QPushButton, QFileDialog, QDialog, QListWidget
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

from .socket_listener import stop_listener
from .global_vars import set_asset_settings, get_asset_settings_default, get_tex_list
from .logging_setup import set_log


window_instance = None


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("LBridge LiveLink Configuration")
        # Qt6: use WindowType for flags
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

        lay_main = QVBoxLayout()

        lay_main.addWidget(Widget_OperatorPath(parent=self))
        lay_main.addWidget(Widget_GeoSetup(parent=self))
        lay_main.addWidget(Widget_ShaderSetup(parent=self))

        # Main widget setup
        widget_main = QWidget()
        widget_main.setLayout(lay_main)

        self.setCentralWidget(widget_main)

    def closeEvent(self, state):
        stop_listener()
        default_settings = get_asset_settings_default()
        for k, v in default_settings.items():
            set_asset_settings(k, v)


class Widget_ShaderSetup(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        lay_main = QVBoxLayout()
        lay_main.setSpacing(5)
        lay_main.setContentsMargins(15, 15, 15, 15)
        group_main = QGroupBox("Shader Setup:")
        lay_main_group = QVBoxLayout()
        lay_main_group.setSpacing(15)
        group_main.setLayout(lay_main_group)

        # Add Shader
        group_shader = QGroupBox("Shader:")
        lay_main_shader = QVBoxLayout()
        lay_main_shader.setSpacing(7.5)
        group_shader.setLayout(lay_main_shader)

        self.use_shader = QCheckBox("Add Shader")
        self.use_shader.setCheckState(Qt.CheckState.Checked)
        self.use_shader.clicked.connect(partial(self.update_use_shader))
        self.use_shader.stateChanged.connect(self.toggle_add_shader)
        lay_main_shader.addWidget(self.use_shader)

        # Custom Shader
        self.use_custom = QCheckBox("Use Custom Shader")
        self.use_custom.clicked.connect(partial(self.update_use_custom))
        self.use_custom.stateChanged.connect(self.toggle_use_custom)
        lay_main_shader.addWidget(self.use_custom)

        # Which Texture to use
        lay_main_tex_sel = QVBoxLayout()
        lay_main_tex_sel.setSpacing(0)
        self.label_use_tex = QLabel("Which Textures to Use:")
        lay_main_tex_sel.addWidget(self.label_use_tex)

        self.lay_use_tex_check = QHBoxLayout()
        tex_list = get_tex_list()
        for tex in tex_list:
            checkbox = QCheckBox(tex)
            checkbox.setCheckState(Qt.CheckState.Checked)
            checkbox.clicked.connect(partial(self.update_use_tex, checkbox))
            self.lay_use_tex_check.addWidget(checkbox)
            setattr(self, f"use_{tex}", checkbox)

        lay_main_tex_sel.addLayout(self.lay_use_tex_check)
        lay_main_shader.addLayout(lay_main_tex_sel)
        lay_main_group.addWidget(group_shader)

        # Texture Conversion
        group_convert = QGroupBox("Convert Textures:")
        lay_main_convert = QVBoxLayout()
        group_convert.setLayout(lay_main_convert)

        self.use_convert = QCheckBox("Convert Textures")
        self.use_convert.clicked.connect(partial(self.update_use_convert))
        self.use_convert.stateChanged.connect(self.toggle_use_convert)
        lay_main_convert.addWidget(self.use_convert)

        self.format_label = QLabel("Convert to Image format:")
        lay_main_convert.addWidget(self.format_label)
        self.format = QComboBox()
        self.format.addItems([".rat", ".exr"])
        self.format.currentIndexChanged.connect(partial(self.update_format))
        self.format.setEnabled(False)
        lay_main_convert.addWidget(self.format)

        self.space_label = QLabel("Output Color Space:")
        lay_main_convert.addWidget(self.space_label)
        self.space = QComboBox()
        self.space.addItems(["ACEScg", "sRGB (No convertion)"])
        self.space.currentIndexChanged.connect(partial(self.update_space))
        self.space.setEnabled(False)
        lay_main_convert.addWidget(self.space)
        lay_main_group.addWidget(group_convert)

        lay_main.addWidget(group_main)
        self.setLayout(lay_main)

    def toggle_add_shader(self, state):
        check = (state == Qt.CheckState.Checked) and (self.use_custom.checkState() != Qt.CheckState.Checked)
        layout = self.lay_use_tex_check
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if widget:
                widget.setEnabled(check)

        self.use_custom.setEnabled(state == Qt.CheckState.Checked)

    def toggle_use_custom(self, state):
        layout = self.lay_use_tex_check
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if widget:
                widget.setEnabled(state != Qt.CheckState.Checked)

    def update_use_shader(self):
        set_asset_settings("use_shader", self.use_shader.isChecked())

    def update_use_custom(self):
        set_asset_settings("use_custom_shader", self.use_custom.isChecked())

    def update_use_tex(self, checkbox):
        checked = checkbox.isChecked()
        tex: str = checkbox.text()
        set_asset_settings(f"use_{tex.lower()}", checked)

    def toggle_use_convert(self, state):
        enabled = state == Qt.CheckState.Checked
        self.format.setEnabled(enabled)
        self.space.setEnabled(enabled)

    def update_use_convert(self):
        set_asset_settings("use_rat", self.use_convert.isChecked())

    def update_format(self, index):
        set_asset_settings("convert_ext", index)

    def update_space(self, index):
        set_asset_settings("convert_space", index)


class Widget_GeoSetup(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        lay_main = QVBoxLayout()
        lay_main.setSpacing(0)
        lay_main.setContentsMargins(15, 15, 15, 15)
        group_main = QGroupBox("Geometry Setup:")
        lay_main_group = QVBoxLayout()
        lay_main_group.setSpacing(15)
        group_main.setLayout(lay_main_group)

        # Default LOD
        group_lod = QGroupBox("LODs:")
        lay_main_lod = QVBoxLayout()
        group_lod.setLayout(lay_main_lod)

        self.lod_label = QLabel("Default LOD:")
        lay_main_lod.addWidget(self.lod_label)

        self.lod = QComboBox()
        self.lod.addItems(["High", "LOD0", "LOD1", "LOD2", "LOD3", "LOD4", "LOD5"])
        self.lod.setCurrentIndex(1)
        self.lod.currentIndexChanged.connect(partial(self.update_lod))
        lay_main_lod.addWidget(self.lod)

        lay_main_group.addWidget(group_lod)

        # Use Proxy
        group_prox = QGroupBox("Proxy:")
        lay_main_prox = QVBoxLayout()
        group_prox.setLayout(lay_main_prox)

        self.use_prox = QCheckBox("Add Proxy")
        self.use_prox.setCheckState(Qt.CheckState.Checked)
        self.use_prox.clicked.connect(partial(self.update_use_prox))
        self.use_prox.stateChanged.connect(self.toggle_prox_type)
        lay_main_prox.addWidget(self.use_prox)

        # Proxy Type
        lay_prox_type = QVBoxLayout()
        prox_type_label = QLabel("Proxy Type:")
        lay_prox_type.addWidget(prox_type_label)

        self.prox_type = QComboBox()
        self.prox_type.addItems(["Bounding Box", "Pyramid", "Poly Reduced", "Custom"])
        self.prox_type.currentIndexChanged.connect(partial(self.update_prox_type))
        lay_prox_type.addWidget(self.prox_type)
        lay_main_prox.addLayout(lay_prox_type)

        lay_main_group.addWidget(group_prox)

        lay_main.addWidget(group_main)

        self.setLayout(lay_main)

    def toggle_prox_type(self, state):
        self.prox_type.setEnabled(state == Qt.CheckState.Checked)

    def update_lod(self, index):
        set_asset_settings("lod", index)

    def update_use_prox(self):
        set_asset_settings("use_prox", self.use_prox.isChecked())

    def update_prox_type(self, index):
        set_asset_settings("prox_type", index)


class Widget_OperatorPath(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        lay_main = QVBoxLayout()
        group_main = QGroupBox("Root Path:")
        lay_main_group = QVBoxLayout()
        group_main.setLayout(lay_main_group)

        self.path_warning = QLabel("", self)
        font = QFont()
        font.setPointSize(12)
        # font.setBold(True)
        self.path_warning.setFont(font)
        self.path_warning.setStyleSheet("color: red;")
        self.path_warning.setVisible(False)
        lay_main_group.addWidget(self.path_warning)

        self.root_edit = QLineEdit(self)
        self.root_edit.setText("/obj/quixel_assets")
        self.root_edit.textChanged.connect(partial(self.update_root))
        self.root_edit.textChanged.connect(self.check_if_path_exists)
        lay_main_group.addWidget(self.root_edit)

        self.browse_button = QPushButton("Browse", self)
        self.browse_button.clicked.connect(self.open_operator_path_dialog)
        lay_main_group.addWidget(self.browse_button)

        lay_main.addWidget(group_main)

        self.setLayout(lay_main)

    def update_root(self, text):
        set_asset_settings("root", text)

    def check_if_path_exists(self, text):
        node = hou.node(text)
        if not node:
            self.path_warning.setVisible(True)
            self.path_warning.setText(
                "Warning: Node at Path does not exist or can not hold child Nodes.\n"
                "Assets will be exported to Path: /obj/quixel_assets"
            )

        elif not node.isNetwork():
            self.path_warning.setVisible(True)
            self.path_warning.setText(
                "Warning: Node at Path is not a Network and can not hold child Nodes.\n"
                "Assets will be exported to Path: /obj/quixel_assets"
            )

        elif not node.isEditable():
            self.path_warning.setVisible(True)
            self.path_warning.setText(
                "Warning: Node at Path is Locked.\n"
                "Assets will be exported to Path: /obj/quixel_assets"
            )

        elif node.childTypeCategory().name() != "Lop":
            self.path_warning.setVisible(True)
            self.path_warning.setText(
                "Warning: Node at Path is not of type Lop.\n"
                "Assets will be exported to Path: /obj/quixel_assets"
            )

        else:
            self.path_warning.setVisible(False)

    def open_operator_path_dialog(self):
        dialog = OperatorPathDialog(self)
        # Qt6: exec_() -> exec(), and check DialogCode
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.root_edit.setText(dialog.selected_path)


class OperatorPathDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Select Operator Path")

        layout = QVBoxLayout()

        # Create a QTreeWidget to display hierarchical operator paths
        self.path_tree = QTreeWidget(self)
        self.path_tree.setHeaderLabel("Operator Paths")
        layout.addWidget(self.path_tree)

        # Dynamically fetch operator paths and populate the tree
        operator_paths = self.get_operator_paths()
        self.populate_tree(operator_paths)

        # OK and Cancel buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK", self)
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)

        cancel_button = QPushButton("Cancel", self)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.selected_path = ""

    def get_operator_paths(self):
        """
        Fetch all operator (node) paths in the current Houdini session.
        Modify this method to filter specific node types or categories.
        """
        operator_paths = []
        # Get all nodes in the current Houdini scene
        for node in hou.node("/").allSubChildren():
            operator_paths.append(node.path())
        return operator_paths

    def populate_tree(self, operator_paths):
        """
        Populate the QTreeWidget with operator paths in a hierarchical structure.
        """
        root_items = {}

        for path in operator_paths:
            parts = path.split("/")
            parent_item = self.path_tree

            for i, part in enumerate(parts):
                # Skip empty parts (e.g., the first "/" split)
                if not part:
                    continue

                # Build the path up to this part
                current_path = "/".join(parts[:i + 1])

                # Check if this part already exists in the tree
                if current_path not in root_items:
                    # Create a new tree item for this part
                    item = QTreeWidgetItem([part])
                    if parent_item == self.path_tree:
                        self.path_tree.addTopLevelItem(item)
                    else:
                        parent_item.addChild(item)
                    root_items[current_path] = item

                # Move to the next level (this part becomes the new parent)
                parent_item = root_items[current_path]

        # Collapse all items by default
        self.path_tree.collapseAll()

    def accept(self):
        # Get the selected path when the user clicks OK
        selected_item = self.path_tree.currentItem()
        if selected_item:
            # Traverse back up the tree to get the full path
            path_parts = []
            item = selected_item
            while item:
                path_parts.insert(0, item.text(0))
                item = item.parent()
            self.selected_path = "/" + "/".join(path_parts)
        super().accept()


def init_window():
    try:
        global window_instance
        window_instance = MainWindow()
        window_instance.show()
    except Exception as e:
        set_log("Error initializing Import Options Window", exc_info=sys.exc_info())
        raise e
