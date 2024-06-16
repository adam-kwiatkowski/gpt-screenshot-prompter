from PIL import Image, ImageGrab
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QPainter, QBrush, QColor, QPen, QIcon
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton


class RegionSelectOverlay(QWidget):
    overlay_closed = pyqtSignal(list)
    screenshot: Image

    def __init__(self):
        super().__init__()
        self.region_start = None
        self.region_end = None
        self.switch_options = [[]]
        self.choices = []
        self.square_size = 50
        self.level = 0

        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(0, 0, self.screen().geometry().width(), self.screen().geometry().height())

        self.label = QLabel(self)
        self.label.setText("Click and drag to select region.")
        self.label.setStyleSheet("QLabel { color : white; font-size: 30px; }")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setGeometry(0, 0, self.screen().geometry().width(), 100)

        self.setMouseTracking(True)

        self.show()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor(0, 0, 0, 128)))
        painter.drawRect(self.rect())
        if self.region_start and self.region_end:
            painter.setBrush(QBrush(QColor(255, 255, 255, 55)))
            painter.drawRect(self.region_start[0], self.region_start[1], self.region_end[0] - self.region_start[0],
                             self.region_end[1] - self.region_start[1])

    def mousePressEvent(self, event):
        self.region_start = (event.pos().x(), event.pos().y())
        self.update()

    def mouseMoveEvent(self, event):
        self.region_end = (event.pos().x(), event.pos().y())
        self.update()

    def mouseReleaseEvent(self, event):
        if self.region_start == self.region_end:
            self.region_start = None
            self.region_end = None
            self.update()
            return

        if self.region_end[0] < self.region_start[0]:
            x = self.region_start[0]
            self.region_start = (self.region_end[0], self.region_start[1])
            self.region_end = (x, self.region_end[1])

        if self.region_end[1] < self.region_start[1]:
            y = self.region_start[1]
            self.region_start = (self.region_start[0], self.region_end[1])
            self.region_end = (self.region_end[0], y)

        selected_region = (self.region_start, self.region_end)
        self.region_start = None
        self.region_end = None
        bbox = [selected_region[0][0], selected_region[0][1], selected_region[1][0], selected_region[1][1]]
        self.overlay_closed.emit(bbox)

        self.update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.overlay_closed.emit([])
            self.close()
