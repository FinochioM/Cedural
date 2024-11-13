from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QCheckBox, QSpinBox, QComboBox, QGroupBox,
                               QListWidget, QPushButton, QScrollArea)
from PySide6.QtCore import Signal, Qt


class CategoryRulesEditor(QWidget):
    rulesChanged = Signal(dict)  # Emits when rules_managers are modified

    def __init__(self, category_manager):
        super().__init__()
        self.category_manager = category_manager
        self.current_category = None
        self.rules = {}  # Format: {category_name: {rule_type: value}}
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # Rules scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        rules_widget = QWidget()
        self.rules_layout = QVBoxLayout(rules_widget)

        # Connectivity Rules
        connectivity_group = QGroupBox("Connectivity Rules")
        connectivity_layout = QVBoxLayout()

        self.must_be_connected = QCheckBox("Must be connected")
        self.must_be_connected.stateChanged.connect(self.update_rules)
        connectivity_layout.addWidget(self.must_be_connected)

        connectivity_group.setLayout(connectivity_layout)
        self.rules_layout.addWidget(connectivity_group)

        # Neighbor Rules
        neighbors_group = QGroupBox("Allowed Neighbors")
        neighbors_layout = QVBoxLayout()

        self.neighbors_list = QListWidget()
        self.neighbors_list.setSelectionMode(QListWidget.MultiSelection)
        self.neighbors_list.itemSelectionChanged.connect(self.update_rules)
        neighbors_layout.addWidget(self.neighbors_list)

        neighbors_group.setLayout(neighbors_layout)
        self.rules_layout.addWidget(neighbors_group)

        # Percentage Rules
        percentage_group = QGroupBox("Percentage Rules")
        percentage_layout = QVBoxLayout()

        # Min percentage
        min_layout = QHBoxLayout()
        min_layout.addWidget(QLabel("Minimum Percentage:"))
        self.min_percentage = QSpinBox()
        self.min_percentage.setRange(0, 100)
        self.min_percentage.valueChanged.connect(self.update_rules)
        min_layout.addWidget(self.min_percentage)
        percentage_layout.addLayout(min_layout)

        # Max percentage
        max_layout = QHBoxLayout()
        max_layout.addWidget(QLabel("Maximum Percentage:"))
        self.max_percentage = QSpinBox()
        self.max_percentage.setRange(0, 100)
        self.max_percentage.setValue(100)
        self.max_percentage.valueChanged.connect(self.update_rules)
        max_layout.addWidget(self.max_percentage)
        percentage_layout.addLayout(max_layout)

        percentage_group.setLayout(percentage_layout)
        self.rules_layout.addWidget(percentage_group)

        scroll.setWidget(rules_widget)
        main_layout.addWidget(scroll)

        # Style
        self.setStyleSheet("""
            QGroupBox {
                border: 1px solid #454545;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                color: #CCCCCC;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 10px;
            }
            QLabel {
                color: #CCCCCC;
            }
            QCheckBox {
                color: #CCCCCC;
            }
            QSpinBox {
                background-color: #1E1E1E;
                color: #CCCCCC;
                border: 1px solid #454545;
            }
            QListWidget {
                background-color: #1E1E1E;
                color: #CCCCCC;
                border: 1px solid #454545;
            }
        """)

    def update_category_list(self, categories):
        """Update the available categories for neighbor selection"""
        self.neighbors_list.clear()
        for category in categories:
            self.neighbors_list.addItem(category)

    def update_rules(self):
        """Collect all rules_managers into a dictionary and emit signal"""
        if not self.current_category:
            return

        # Collect rules_managers
        rules = {
            "mustBeConnected": self.must_be_connected.isChecked(),
            "allowedNeighbors": [item.text() for item in
                                 self.neighbors_list.selectedItems()],
            "minPercentage": self.min_percentage.value(),
            "maxPercentage": self.max_percentage.value()
        }

        # Update rules_managers dictionary
        self.rules[self.current_category] = rules
        self.rulesChanged.emit(self.rules)

    def load_category_rules(self, category_name):
        """Load rules_managers for selected category"""
        self.current_category = category_name

        if category_name in self.rules:
            rules = self.rules[category_name]
            self.must_be_connected.setChecked(rules.get("mustBeConnected", False))

            # Update neighbor selection
            for i in range(self.neighbors_list.count()):
                item = self.neighbors_list.item(i)
                item.setSelected(item.text() in rules.get("allowedNeighbors", []))

            self.min_percentage.setValue(rules.get("minPercentage", 0))
            self.max_percentage.setValue(rules.get("maxPercentage", 100))
        else:
            # Reset to defaults if no rules_managers exist
            self.must_be_connected.setChecked(False)
            self.min_percentage.setValue(0)
            self.max_percentage.setValue(100)
            for i in range(self.neighbors_list.count()):
                self.neighbors_list.item(i).setSelected(False)