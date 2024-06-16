from PyQt5 import Qt
from PyQt5.QtWidgets import QWidget, QScrollArea, QLabel, QVBoxLayout


class ScrollableTextWidget(QScrollArea):
    def __init__(self, *args, **kwargs):
        QScrollArea.__init__(self, *args, **kwargs)

        self.setWidgetResizable(True)

        content = QWidget(self)
        self.setWidget(content)

        lay = QVBoxLayout(content)

        self.label = QLabel(content)

        self.label.setAlignment(Qt.Qt.AlignLeft | Qt.Qt.AlignTop)

        self.label.setWordWrap(True)

        self.label.setTextInteractionFlags(Qt.Qt.TextSelectableByMouse)

        lay.addWidget(self.label)

    def text(self):
        return self.label.text()

    def setText(self, text):
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())
        self.label.setText(text)
