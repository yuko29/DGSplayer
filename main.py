from PyQt5 import QtWidgets
from controller import MainWindow
# from gui.main_ui import Ui_MainWindow
import sys




if __name__ == '__main__': 
    app = QtWidgets.QApplication(sys.argv)
    # Mainwindow = QtWidgets.QMainWindow()
    # ui = Ui_MainWindow() 
    # ui.setupUi(Mainwindow)
    window = MainWindow()
    # window = Ui_MainWindow()
    # window.show()
    window.ui.show()
    sys.exit(app.exec_())