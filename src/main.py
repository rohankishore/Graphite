import sys
import qdarktheme
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QApplication, QMainWindow, QDockWidget, QVBoxLayout, QWidget, QLineEdit, QListWidget, \
    QAbstractItemView, QToolBar, QStatusBar, QSizePolicy, QMenu, QHBoxLayout, QPushButton, QCompleter
from PyQt6.QtCore import Qt
from GraphWidget import MatplotlibWidget
import values

class Graphite(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Graphyte.")
        self.setWindowIcon(QIcon("resources/icons/icon_black.ico"))
        self.setGeometry(100, 100, 800, 600)

        self.toolbox = QToolBar(self)
        self.toolbox.setFixedHeight(40)
        # self.addToolBar(self.toolbox)

        self.bottom_bar = QStatusBar()
        #self.setStatusBar(self.bottom_bar)

        move_menu = QMenu(self)
        move_menu.addAction("Pan", self._move)
        move_menu.addAction("Zoom", self._zoom)

        circle_menu = QMenu(self)
        circle_menu.addAction("Circle with Center and Radius")

        move = QAction("Move", self)
        move.setMenu(move_menu)
        move.triggered.connect(self._move)
        move.setIcon(QIcon("resources/icons/move.png"))

        save = QAction("Save", self)
        save.triggered.connect(self._save)
        save.setIcon(QIcon("resources/icons/save.png"))

        circle = QAction("Circle", self)
        circle.setMenu(circle_menu)
        circle.triggered.connect(self._move)
        circle.setIcon(QIcon("resources/icons/circle.png"))

        # Add actions to the toolbar
        self.toolbox.addAction(move)
        self.toolbox.addSeparator()
        self.toolbox.addAction(circle)
        self.toolbox.addSeparator()
        self.toolbox.addAction(save)

        # Create the central widget that holds the graphing area and input bar
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Layout for the central widget
        central_layout = QVBoxLayout()
        self.central_widget.setLayout(central_layout)

        # Create the dock widget for the left panel
        self.dock_widget = QDockWidget("Functions", self)

        # Create a widget for the dock widget
        dock_widget_contents = QWidget()
        dock_layout = QVBoxLayout()
        dock_widget_contents.setLayout(dock_layout)

        # Create a QListWidget to display function names
        self.function_list_widget = QListWidget()
        self.function_list_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.function_list_widget.itemSelectionChanged.connect(
            self.listboxActions)  # Connect to remove function
        dock_layout.addWidget(self.function_list_widget)

        # Set the contents of the dock widget
        self.dock_widget.setWidget(dock_widget_contents)

        # Add the dock widget to the main window
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock_widget)

        # Create the graphing area on the right
        self.graph_widget = MatplotlibWidget(self)
        central_layout.addWidget(self.toolbox)
        central_layout.addWidget(self.graph_widget)

        # Add a stretchable spacer to fill the status bar
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self.bottom_bar.addWidget(spacer)

        self.input_layout = QHBoxLayout()

        # Create the input bar
        self.input_bar = QLineEdit()
        self.completer = QCompleter(values.functions)
        self.completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.completer.activated.connect(self.on_completer_activated)
        self.input_bar.setCompleter(self.completer)
        self.input_bar.setPlaceholderText("Input: ")
        self.input_bar.returnPressed.connect(self.on_return_pressed)
        self.input_layout.addWidget(self.input_bar)

        # Create the keyboard button
        self.keyboard_button = QPushButton()
        keyboard_icon = QIcon("resources/icons/keyboard.png")
        self.keyboard_button.setIcon(keyboard_icon)
        self.keyboard_button.setMinimumSize(50, 50)
        self.input_layout.addWidget(self.keyboard_button)

        # Now add the input layout to the central layout
        central_layout.addLayout(self.input_layout)

        self.bottom_bar.addWidget(spacer)
        #self.bottom_bar.addWidget(self.input_bar)
        # self.bottom_bar.addWidget(self.input_bar)

        # List to hold user-entered functions
        self.functions = []

    def listboxActions(self):
        delete_action = QAction("Delete", self)
        delete_action.setShortcut(Qt.Key.Key_Delete)
        delete_action.triggered.connect(self.remove_selected_function)
        self.addAction(delete_action)

    def on_completer_activated(self, completion):
        """
        This method is called when an auto-complete suggestion is selected.
        """
        self.input_bar.setText(completion)
        # Optional: Trigger graph update when selecting from completer, if desired
        # self.update_graph()  # You can decide if you want this behavior

    def on_return_pressed(self):
        """
        This method is called when Enter/Return is pressed.
        Trigger graph update only if input wasn't from the completer.
        """
        # Check if completer's popup is visible (indicating a selection is in progress)
        if self.completer.popup().isVisible():
            return  # Ignore 'returnPressed' when completer is visible

        self.update_graph()  # Trigger the graph update

    def update_graph(self):
        function_text = self.input_bar.text()
        self.functions.append(function_text)
        self.function_list_widget.addItem(function_text)
        self.graph_widget.plot_function(self.functions)

    def _move(self):
        self.graph_widget.toolbar.pan(True)

    def _zoom(self):
        self.graph_widget.toolbar.zoom(True)

    def _save(self):
        self.graph_widget.toolbar.save_figure()

    def remove_selected_function(self):
        selected_items = self.function_list_widget.selectedItems()
        if selected_items:
            selected_item_text = selected_items[0].text()
            row = self.function_list_widget.row(selected_items[0])
            self.function_list_widget.takeItem(row)
            self.functions.remove(selected_item_text)
            f = ["sin(x)", "cos(x)"]
            self.graph_widget.plot_function(self.functions)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Graphite()
    window.showMaximized()
    qdarktheme.setup_theme("dark")
    window.show()
    sys.exit(app.exec())