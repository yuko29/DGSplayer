from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QMainWindow, QMessageBox, 
                            QSlider, QLabel, QLineEdit, QPushButton, QVBoxLayout, 
                            QHBoxLayout, QFrame, QSplitter, QComboBox, QPlainTextEdit, QListWidget,
                            QStackedLayout)
from PyQt5.QtCore import Qt, QUrl, QTimer
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
import os, random, time, re
from pymongo import MongoClient
import configparser

class MainUI(QMainWindow):
    
    def __init__(self, parent=None):
        super(MainUI, self).__init__(parent=parent)
        
        self.settingfilename = '/Users/huyufang/Projects/DGSplayer/config.ini'
        self.loadingSetting()
        self.initUI()
        
        
    def initUI(self):      
        
        # left frame
        self.left_frame = QFrame(self)  
        self.left_frame.setFrameShape(QFrame.StyledPanel)
        self.left_StackedLayout = QStackedLayout(self.left_frame)
        self.btn_tmp = QPushButton(self.left_frame)
        self.btn_tmp.setText("開播！")
        self.btn_tmp.pressed.connect(self.show_play_list)
        self.musicList = QListWidget()
        self.musicList.setSortingEnabled(True)
        self.musicList.itemDoubleClicked.connect(self.doubleClicked)
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
        self.prevBtn = QPushButton(' Last song ', self)
        self.nextBtn = QPushButton(' Next song ', self)
        self.openBtn = QPushButton(' Open folder ', self)
        self.playBtn.clicked.connect(self.playMusic)
        self.prevBtn.clicked.connect(self.prevMusic)
        self.nextBtn.clicked.connect(self.nextMusic)
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
        self.hBoxButton.addWidget(self.nextBtn)
        self.hBoxButton.addWidget(self.prevBtn)
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
        self.submit_btn.clicked.connect(self.saveContent)
        self.bottom_layout.addLayout(self.ttl_line_layout)
        self.bottom_layout.addWidget(self.content)
        self.bottom_layout.addWidget(self.submit_btn, alignment=Qt.AlignRight)
        
        splitter1 = QSplitter(Qt.Vertical)
        splitter1.addWidget(self.top_right_frame)
        splitter1.addWidget(self.bottom_frame)

        splitter2 = QSplitter(Qt.Horizontal)
        splitter2.addWidget(self.left_frame)
        splitter2.addWidget(splitter1)
        
        #self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('DGS player')
        
        self.setCentralWidget(splitter2)

        # self.cur_path = "/Users/huyufang/DGS"
        self.song_formats = ['mp3', 'm4a', 'aac']
        self.songs_list = []
        self.cur_playing_song = ''
        self.is_pause = True
    
        self.player = QMediaPlayer()
        self.is_switching = False
        self.timer = QTimer(self)
        self.timer.start(1000)
        self.timer.timeout.connect(self.playByMode)
        self.slider.sliderMoved[int].connect(lambda: self.player.setPosition(self.slider.value()))
         


    #  Load profile 
    def loadingSetting(self):
        config = configparser.ConfigParser()
        config.read(self.settingfilename)
        if not os.path.isfile(self.settingfilename):
            return
        self.cur_path = config.get('MusicDir', 'PATH')
        self.db_uri = config.get('Database', 'uri')
        self.db_client = MongoClient(self.db_uri)
        self.db = self.db_client[config.get('Database', 'dbname')]
        self.db_collect = self.db[config.get('Database', 'collection')]

    # Write and play the currently set music function ：
    def setCurPlaying(self):
        # cur_playing_song is the whole path to the file
        self.cur_playing_song = self.songs_list[self.musicList.currentRow()][-1]
        self.player.setMedia(QMediaContent(QUrl.fromLocalFile(self.cur_playing_song)))
        regex = re.compile(r'/(\w+)\.aac')
        file = regex.search(self.cur_playing_song).group(1)
        self.cur_play_title.setText(file)
        self.loadContent(file)
    
    def playMusic(self):
        if self.musicList.count() == 0:
            self.Tips(' There is no music file to play in the current path ')
            return
        if not self.player.isAudioAvailable():
            self.setCurPlaying()
        if self.is_pause or self.is_switching:
            self.player.play()
            self.is_pause = False
            self.playBtn.setText(' Pause ')
        elif (not self.is_pause) and (not self.is_switching):
            self.player.pause()
            self.is_pause = True
            self.playBtn.setText(' Play ')
    def prevMusic(self):
        self.slider.setValue(0)
        if self.musicList.count() == 0:
            self.Tips(' There is no music file to play in the current path ')
            return
        pre_row = self.musicList.currentRow()-1 if self.musicList.currentRow() != 0 else self.musicList.count() - 1
        self.musicList.setCurrentRow(pre_row)
        self.is_switching = True
        self.setCurPlaying()
        self.playMusic()
        self.is_switching = False
    
    def nextMusic(self):
        self.slider.setValue(0)
        if self.musicList.count() == 0:
            self.Tips(' There is no music file to play in the current path ')
            return
        next_row = self.musicList.currentRow()+1 if self.musicList.currentRow() != self.musicList.count()-1 else 0
        self.musicList.setCurrentRow(next_row)
        self.is_switching = True
        self.setCurPlaying()
        self.playMusic()
        self.is_switching = False
    
    def doubleClicked(self):
        self.slider.setValue(0)
        self.is_switching = True
        self.setCurPlaying()
        self.playMusic()
        self.is_switching = False
    
    #  Play automatically according to play mode , And refresh the progress bar 
    def playByMode(self):
        self.player.setVolume(self.volumeSlider.value())
        #  Refresh progress bar 
        if (not self.is_pause) and (not self.is_switching):
            self.slider.setMinimum(0)
            self.slider.setMaximum(self.player.duration())
            self.slider.setValue(self.slider.value() + 1000)
        self.startTimeLabel.setText(time.strftime('%M:%S', time.localtime(self.player.position()/1000)))
        self.endTimeLabel.setText(time.strftime('%M:%S', time.localtime(self.player.duration()/1000)))
        #  Order of play 
        if (self.modeCom.currentIndex() == 0) and (not self.is_pause) and (not self.is_switching):
            if self.musicList.count() == 0:
                return
            if self.player.position() == self.player.duration():
                self.nextMusic()
        #  Single tune circulation 
        elif (self.modeCom.currentIndex() == 1) and (not self.is_pause) and (not self.is_switching):
            if self.musicList.count() == 0:
                return
            if self.player.position() == self.player.duration():
                self.is_switching = True
                self.setCurPlaying()
                self.slider.setValue(0)
                self.playMusic()
                self.is_switching = False
        #  Random broadcast 
        elif (self.modeCom.currentIndex() == 2) and (not self.is_pause) and (not self.is_switching):
            if self.musicList.count() == 0:
                return
            if self.player.position() == self.player.duration():
                self.is_switching = True
                self.musicList.setCurrentRow(random.randint(0, self.musicList.count()-1))
                self.setCurPlaying()
                self.slider.setValue(0)
                self.playMusic()
                self.is_switching = False

    def show_play_list(self):
        self.musicList.clear()
        for song in os.listdir(self.cur_path):
            if song.split('.')[-1] in self.song_formats:
                self.songs_list.append([song, os.path.join(self.cur_path, song).replace('\\', '/')])
                self.musicList.addItem(song)
        self.songs_list.sort()
        self.musicList.setCurrentRow(0)
        if self.songs_list:
                self.cur_playing_song = self.songs_list[self.musicList.currentRow()][-1]
        self.left_StackedLayout.setCurrentIndex(1)
    
    def volumeChange(self):
        self.sound_effect.setVolume(self.slider.value()/10)

    def loadContent(self, file):
        result = self.db_collect.find_one({'file': file})
        if result is not None:
            self.title_input.setText(result['title'])
            self.content.setPlainText(result['content'])
        else:
            self.title_input.setText('')
            self.content.setPlainText('')
    
    def saveContent(self):
        if self.db_collect.find_one({'file': self.cur_play_title.text()}) is None:
            self.db_collect.insert_one({'file': self.cur_play_title.text(), 'title': self.title_input.text(), 'content': self.content.toPlainText()})
        else:
            self.db_collect.update_one({'file': self.cur_play_title.text()}, {"$set": {'title': self.title_input.text(), 'content': self.content.toPlainText()}})


    #  Confirm if the user really wants to exit 
    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message',
            " Are you sure you want to quit ？", QMessageBox.Yes | 
            QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()



