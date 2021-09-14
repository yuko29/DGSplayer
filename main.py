from PyQt5.QtWidgets import QApplication
from gui.main_ui import MainUI
import sys

if __name__ == '__main__': 
    app = QApplication(sys.argv)
    gui = MainUI()
    gui.show()
    sys.exit(app.exec_())