from PyQt5 import QtWidgets, QtGui
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import Qt, QUrl, QTimer
from PyQt5.QtWidgets import QMessageBox
from gui.main_ui import Ui_MainWindow
import configparser
from pymongo import MongoClient
import os, random, time, re

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.setup_control()
        
    
    def setup_control(self):
        self.settingfilename = '/Users/huyufang/Projects/DGSplayer/config.ini'
        self.loadingSetting()
        self.ui.btn_tmp.pressed.connect(self.show_play_list)
        self.ui.musicList.itemDoubleClicked.connect(self.doubleClicked)
        self.ui.playBtn.clicked.connect(self.playMusic)
        self.ui.prevBtn.clicked.connect(self.prevMusic)
        self.ui.nextBtn.clicked.connect(self.nextMusic)
        self.ui.submit_btn.clicked.connect(self.saveContent)
        self.player = QMediaPlayer()
        self.is_switching = False
        self.timer = QTimer(self)
        self.timer.start(1000)
        self.timer.timeout.connect(self.playByMode)
        self.ui.slider.sliderMoved[int].connect(lambda: self.player.setPosition(self.ui.slider.value()))
        # self.cur_path = "/Users/huyufang/DGS"
        self.song_formats = ['mp3', 'm4a', 'aac']
        self.songs_list = []
        self.cur_playing_song = ''
        self.is_pause = True 
    
    
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
    
    # Switch to the select song and disply its information
    def setCurPlaying(self):
        # cur_playing_song is the whole path to the file
        self.cur_playing_song = self.songs_list[self.ui.musicList.currentRow()][-1]
        self.player.setMedia(QMediaContent(QUrl.fromLocalFile(self.cur_playing_song)))
        regex = re.compile(r'/(\w+)\.\w+$')
        file = regex.search(self.cur_playing_song).group(1)
        self.ui.cur_play_title.setText(file)   # set the title
        self.loadSongContent(file)              # load the text content
    
    def playMusic(self):
        if self.ui.musicList.count() == 0:
            self.Tips(' There is no music file to play in the current path ')
            return
        if not self.player.isAudioAvailable():
            self.setCurPlaying()
        if self.is_pause or self.is_switching:
            self.player.play()
            self.is_pause = False
            self.ui.playBtn.setText(' Pause ')
        elif (not self.is_pause) and (not self.is_switching):
            self.player.pause()
            self.is_pause = True
            self.ui.playBtn.setText(' Play ')
    
    def prevMusic(self):
        self.ui.slider.setValue(0)
        if self.ui.musicList.count() == 0:
            self.Tips(' There is no music file to play in the current path ')
            return
        pre_row = self.ui.musicList.currentRow()-1 if self.ui.musicList.currentRow() != 0 else self.ui.musicList.count() - 1
        self.ui.musicList.setCurrentRow(pre_row)
        self.is_switching = True
        self.setCurPlaying()
        self.playMusic()
        self.is_switching = False
    
    def nextMusic(self):
        self.ui.slider.setValue(0)
        if self.ui.musicList.count() == 0:
            self.Tips(' There is no music file to play in the current path ')
            return
        next_row = self.ui.musicList.currentRow()+1 if self.ui.musicList.currentRow() != self.ui.musicList.count()-1 else 0
        self.ui.musicList.setCurrentRow(next_row)
        self.is_switching = True
        self.setCurPlaying()
        self.playMusic()
        self.is_switching = False
    
    def doubleClicked(self):
        self.ui.slider.setValue(0)
        self.is_switching = True
        self.setCurPlaying()
        self.playMusic()
        self.is_switching = False
    
    #  Play automatically according to play mode , And refresh the progress bar 
    def playByMode(self):
        self.player.setVolume(self.ui.volumeSlider.value())
        #  Refresh progress bar 
        if (not self.is_pause) and (not self.is_switching):
            self.ui.slider.setMinimum(0)
            self.ui.slider.setMaximum(self.player.duration())
            self.ui.slider.setValue(self.ui.slider.value() + 1000)
        self.ui.startTimeLabel.setText(time.strftime('%M:%S', time.localtime(self.player.position()/1000)))
        self.ui.endTimeLabel.setText(time.strftime('%M:%S', time.localtime(self.player.duration()/1000)))
        #  Order of play 
        if (self.ui.modeCom.currentIndex() == 0) and (not self.is_pause) and (not self.is_switching):
            if self.ui.musicList.count() == 0:
                return
            if self.player.position() == self.player.duration():
                self.nextMusic()
        #  Single tune circulation 
        elif (self.ui.modeCom.currentIndex() == 1) and (not self.is_pause) and (not self.is_switching):
            if self.ui.musicList.count() == 0:
                return
            if self.player.position() == self.player.duration():
                self.is_switching = True
                self.setCurPlaying()
                self.ui.slider.setValue(0)
                self.playMusic()
                self.is_switching = False
        #  Random broadcast 
        elif (self.ui.modeCom.currentIndex() == 2) and (not self.is_pause) and (not self.is_switching):
            if self.ui.musicList.count() == 0:
                return
            if self.player.position() == self.player.duration():
                self.is_switching = True
                self.ui.musicList.setCurrentRow(random.randint(0, self.ui.musicList.count()-1))
                self.setCurPlaying()
                self.ui.slider.setValue(0)
                self.playMusic()
                self.is_switching = False

    def show_play_list(self):
        self.ui.musicList.clear()
        for song in os.listdir(self.cur_path):
            if song.split('.')[-1] in self.song_formats:
                self.songs_list.append([song, os.path.join(self.cur_path, song).replace('\\', '/')])
                self.ui.musicList.addItem(song)
        self.songs_list.sort()
        self.ui.musicList.setCurrentRow(0)
        if self.songs_list:
                self.cur_playing_song = self.songs_list[self.ui.musicList.currentRow()][-1]
        self.ui.left_StackedLayout.setCurrentIndex(1)
    
    def volumeChange(self):
        self.sound_effect.setVolume(self.ui.slider.value()/10)

    def loadSongContent(self, file):
        result = self.db_collect.find_one({'file': file})
        if result is not None:
            self.ui.title_input.setText(result['title'])
            self.ui.content.setPlainText(result['content'])
        else:
            self.ui.title_input.setText('')
            self.ui.content.setPlainText('')
    
    def saveContent(self):
        if self.db_collect.find_one({'file': self.ui.cur_play_title.text()}) is None:
            self.db_collect.insert_one({'file': self.ui.cur_play_title.text(), 'title': self.ui.title_input.text(), 'content': self.ui.content.toPlainText()})
        else:
            self.db_collect.update_one({'file': self.ui.cur_play_title.text()}, {"$set": {'title': self.ui.title_input.text(), 'content': self.ui.content.toPlainText()}})


    #  Confirm if the user really wants to exit 
    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message',
            "Are you sure you want to quit?", QMessageBox.Yes | 
            QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()