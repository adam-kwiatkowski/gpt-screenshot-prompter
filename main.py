import base64
import sys
from io import BytesIO
from pathlib import Path

from PIL import ImageGrab, Image
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QFontDatabase, QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel
from dotenv import load_dotenv
from openai import OpenAI

# noinspection PyUnresolvedReferences
import resources
from widgets.RegionSelectOverlay import RegionSelectOverlay
from widgets.ScrollableTextWidget import ScrollableTextWidget


class OpenAIStreamer(QThread):
    response_chunk = pyqtSignal(str)

    def __init__(self, img_base64):
        super().__init__()
        self.img_base64 = img_base64

    def run(self):
        for response in client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": self.img_base64.decode("utf-8")},
                        }
                    ],
                }
            ],
            max_tokens=300,
            stream=True,
        ):
            self.response_chunk.emit(response.choices[0].delta.content)


class MainWindow(QWidget):
    screenshot: Image

    def __init__(self):
        super().__init__()
        self.thread = None
        self.selected_region = None
        self.overlay = None
        self.screenshot = None

        self.setGeometry(100, 100, 300, 400)
        self.setWindowTitle("GPT Prompter")
        self.setWindowIcon(QIcon(":/icons/ic_launcher.png"))

        layout = QVBoxLayout()

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.show_region_overlay)
        self.start_button.setFixedHeight(35)
        self.start_button.setFont(QFont("Inter", 10))
        self.start_button.setObjectName("primary")
        layout.addWidget(self.start_button)

        self.response_widget = ScrollableTextWidget()
        self.response_widget.setText("Response will appear here.")
        layout.addWidget(self.response_widget)

        self.version_label = QLabel("Adam Kwiatkowski v0.1.0")
        self.version_label.setObjectName("version")
        self.version_label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.version_label)

        self.setLayout(layout)

        self.show()

    def show_region_overlay(self):
        self.screenshot = ImageGrab.grab()
        self.overlay = RegionSelectOverlay()
        self.overlay.show()
        self.overlay.overlay_closed.connect(self.on_region_overlay_closed)

    def on_region_overlay_closed(self, bbox):
        QApplication.restoreOverrideCursor()
        if bbox is None or len(bbox) == 0:
            return
        selected_region = self.screenshot.crop(bbox)
        buffered = BytesIO()
        selected_region.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue())

        img_base64 = bytes("data:image/jpeg;base64,", encoding="utf-8") + img_str

        self.thread = OpenAIStreamer(img_base64)
        self.thread.response_chunk.connect(self.update_response_label)
        self.response_widget.setText("")
        self.thread.start()

        self.overlay = None

    def update_response_label(self, text):
        current_text = self.response_widget.text()
        self.response_widget.setText(current_text + text)


if __name__ == "__main__":
    load_dotenv()
    client = OpenAI()

    app = QApplication(sys.argv)
    QFontDatabase.addApplicationFont(":/fonts/Inter-Regular.ttf")
    app.setStyleSheet(Path("style.qss").read_text())
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
