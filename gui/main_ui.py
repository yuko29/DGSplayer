from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QMainWindow, QWidget,
                            QSlider, QLabel, QLineEdit, QPushButton, QVBoxLayout, 
                            QHBoxLayout, QFrame, QSplitter, QComboBox, QPlainTextEdit, QListWidget,
                            QStackedLayout)
import qdarkstyle

class Ui_MainWindow(QMainWindow):
    
    def __init__(self, parent=None):
        super(Ui_MainWindow, self).__init__(parent=parent)
        self.initUI()
        self.setWindowOpacity(0.9)
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        
        
    def initUI(self):      
        
        # left frame
        self.left_frame = QFrame(self)  
        self.left_frame.setFrameShape(QFrame.StyledPanel)
        self.left_StackedLayout = QStackedLayout(self.left_frame)
        self.btn_tmp = QPushButton(self.left_frame)
        self.btn_tmp.setText("開播！")
        self.musicList = QListWidget()
        self.musicList.setSortingEnabled(True)
        self.left_StackedLayout.addWidget(self.btn_tmp)
        self.left_StackedLayout.addWidget(self.musicList)
        
        # top right frame
        self.top_right_frame = QFrame()
        self.top_right_layout = QVBoxLayout(self.top_right_frame)
        self.cur_play_title = QLabel("OwO", self)
        self.startTimeLabel = QLabel('00:00')
        self.endTimeLabel = QLabel('00:00')
        self.slider = QSlider(Qt.Horizontal, self)
        self.volumeSlider = QSlider(Qt.Horizontal, self)
        self.volumeSlider.setValue(20)
        self.playBtn = QPushButton(' Play ', self)
        self.prevBtn = QPushButton(' Prev song ', self)
        self.nextBtn = QPushButton(' Next song ', self)
        self.openBtn = QPushButton(' Open folder ', self)
        self.modeCom = QComboBox()
        self.modeCom.addItem(' Order of play ')
        self.modeCom.addItem(' Single tune circulation ')
        self.modeCom.addItem(' Random broadcast ')
        self.hBoxSlider = QHBoxLayout()
        self.hBoxSlider.addWidget(self.startTimeLabel)
        self.hBoxSlider.addWidget(self.slider)
        self.hBoxSlider.addWidget(self.endTimeLabel)
        self.hBoxButton = QHBoxLayout()
        self.hBoxButton.addWidget(self.playBtn)
        self.hBoxButton.addWidget(self.prevBtn)
        self.hBoxButton.addWidget(self.nextBtn)
        self.hBoxButton.addWidget(self.modeCom)
        self.hBoxButton.addWidget(self.volumeSlider)
        self.top_right_layout.addWidget(self.cur_play_title)
        self.top_right_layout.addLayout(self.hBoxSlider)
        self.top_right_layout.addLayout(self.hBoxButton)

        # bottom right frame
        self.bottom_frame = QFrame(self)
        self.bottom_layout = QVBoxLayout(self.bottom_frame)
        self.ttl_line_layout = QHBoxLayout()
        self.ttl_label = QLabel('標題',self)
        self.title_input = QLineEdit(self)
        self.ttl_line_layout.addWidget(self.ttl_label)
        self.ttl_line_layout.addWidget(self.title_input)
        self.content = QPlainTextEdit(self)
        self.submit_btn = QPushButton('save', self)
        self.submit_btn.setMaximumWidth(60)
        self.bottom_layout.addLayout(self.ttl_line_layout)
        self.bottom_layout.addWidget(self.content)
        self.bottom_layout.addWidget(self.submit_btn, alignment=Qt.AlignRight)
        
        # export region
        self.export_btn = QPushButton('export', self)
        self.export_btn.setMaximumWidth(60)
        
        splitter1 = QSplitter(Qt.Vertical)
        splitter1.addWidget(self.top_right_frame)
        splitter1.addWidget(self.bottom_frame)

        splitter2 = QSplitter(Qt.Horizontal)
        splitter2.addWidget(self.left_frame)
        splitter2.addWidget(splitter1)
        
        main_widget = QFrame()
        main_widget_layout = QVBoxLayout(main_widget)
        main_widget_layout.addWidget(splitter2)
        main_widget_layout.addWidget(self.export_btn)
        
        #self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('DGS player')
        
        self.setCentralWidget(main_widget)



