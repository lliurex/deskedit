#!/usr/bin/env python3
import sys
import os
from app2menu import App2Menu
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QVBoxLayout,\
				QDialog,QStackedWidget,QGridLayout,QTabWidget,QHBoxLayout,QFormLayout,QLineEdit,QComboBox,\
				QStatusBar,QFileDialog,QDialogButtonBox,QScrollBar,QScrollArea,QCheckBox,QTableWidget,\
				QTableWidgetItem,QHeaderView,QTableWidgetSelectionRange,QListWidget
from PyQt5 import QtGui
from PyQt5.QtCore import QSize,pyqtSlot,Qt, QPropertyAnimation,QThread,QRect,QTimer,pyqtSignal,QSignalMapper
import gettext
import subprocess
gettext.textdomain('deskedit')
_ = gettext.gettext

RSRC="/usr/share/deskedit/rsrc"
RSRC="/home/lliurex/git/desktop-editor/rsrc"

class th_getCategories(QThread):
	signal=pyqtSignal("PyQt_PyObject")
	def __init__(self):
		QThread.__init__(self)

	def __del__(self):
		self.wait()

	def run(self):
		menu=App2Menu.app2menu()
		categories=menu.get_categories()
		self.signal.emit(categories)

class desktopEditor(QWidget):

	def __init__(self,desktop_file=None):
		super().__init__()
		self.dbg=True
		self._debug("Rendering gui...")
		self.categories=[]
		self.icon='exe'
		self.height=0
		desktop=self._read_desktop_file(desktop_file)
		box=QVBoxLayout()
		self.statusBar=QStatusBar()
		self.anim=QPropertyAnimation(self.statusBar, b"geometry")
		self.statusBar.hide()
		self.timer=QTimer()
		self.timer.setSingleShot(True)
		box.addWidget(self.statusBar)
		img_banner=QLabel()
		img=QtGui.QPixmap("%s/deskedit_banner.png"%RSRC)
		img_banner.setPixmap(img)
		box.addWidget(img_banner)
		box.addWidget(self._render_gui(desktop))
		self.setStyleSheet(self._set_css())
		self.setLayout(box)
		self.show()
	#def __init__
	
	def _debug(self,msg):
		if self.dbg:
			print("DeskEdit: %s"%msg)
	#def _debug
	
	def _read_desktop_file(self,desktop_file=None):
		menu=App2Menu.app2menu()
		if desktop_file:
			desktop=menu.get_desktop_info(desktop_file)
		else:
			desktop=menu.init_desktop_file()
		return(desktop)
	#def _read_desktop_file

	def _file_chooser(self,widget=None,path=None,imgDialog=None):
		fdia=QFileDialog()
		fchoosed=''
		fdia.setFileMode(QFileDialog.AnyFile)
		if imgDialog:
			fdia.setNameFilter(_("images(*.png *.xpm *jpg)"))
		else:
			fdia.setNameFilter(_("All files(*.*)"))
		if path:
			self._debug("Set path to %s"%path)
			fdia.setDirectory(path)
		if (fdia.exec_()):
			fchoosed=fdia.selectedFiles()[0]
			if widget:
				if imgDialog:
					self.icon=fdia.selectedFiles()[0]
					icn=QtGui.QIcon(self.icon)
					widget.setIcon(icn)
				else:
					widget.setText(fchoosed)
			return(fchoosed)

	def _render_gui(self,desktop):
		categories=[]
		gui=QWidget()
		gui.setWindowTitle("Appimage Desktop Definition")
		box=QHBoxLayout()
		self.btn_categories={}
		gridBox=QGridLayout()
		self.gridBtnBox=QTableWidget(5,3)
		self.gridBtnBox.horizontalHeader().hide()
		self.gridBtnBox.verticalHeader().hide()
		self.gridBtnBox.setShowGrid(False)
		self.gridBtnBox.setEditTriggers(QTableWidget.NoEditTriggers)
		box.addLayout(gridBox)
		lbl_icon=QLabel(_("Icon: "))
		gridBox.addWidget(lbl_icon,1,2,1,1)
		self.btn_icon=QPushButton()
		self.btn_icon.setObjectName("btnIcon")
		icn_desktop=QtGui.QIcon.fromTheme(self.icon)
		self.btn_icon.setIcon(icn_desktop)
		self.btn_icon.setIconSize(QSize(64,64))
		self.btn_icon.clicked.connect(lambda:self._file_chooser(widget=self.btn_icon,imgDialog=True))
		gridBox.addWidget(self.btn_icon,2,2,3,1)
		lbl_name=QLabel(_("Name: "))
		gridBox.addWidget(lbl_name,1,0,1,2)
		self.inp_name=QLineEdit(desktop['Name'])
		self.inp_name.setPlaceholderText(_("Desktop name"))
		gridBox.addWidget(self.inp_name,2,0,1,2)
		lbl_exec=QLabel(_("Executable: "))
		gridBox.addWidget(lbl_exec,3,0,1,2)
		self.inp_exec=QLineEdit(desktop['Exec'])
		self.inp_exec.setPlaceholderText(_("Executable path"))
		gridBox.addWidget(self.inp_exec,4,0,1,1,Qt.Alignment(0))
		btn_exec=QPushButton("...")
		btn_exec.setObjectName("btnFile")
		btn_exec.clicked.connect(lambda:self._file_chooser(widget=self.inp_exec))
		gridBox.addWidget(btn_exec,4,1,1,1,Qt.Alignment(1))
		lbl_desc=QLabel(_("Description: "))
		gridBox.addWidget(lbl_desc,5,0,1,2)
		self.inp_desc=QLineEdit(desktop['Comment'])
		self.inp_desc.setPlaceholderText(_("Description"))
		gridBox.addWidget(self.inp_desc,6,0,1,2)
		lbl_cat=QLabel(_("Categories: "))
		gridBox.addWidget(lbl_cat,7,0,1,2)
		gridBox.addWidget(self.gridBtnBox,8,0,1,3)
		th_categories=th_getCategories()
		th_categories.start()
		th_categories.signal.connect(self._set_categories)
		btn_load=QPushButton(_("Load"))
		btn_load.clicked.connect(self._load_desktop)
		gridBox.addWidget(btn_load,9,0,1,1,Qt.Alignment(1))
		btn_cancel=QPushButton(_("Cancel"))
		btn_cancel.clicked.connect(self._clear_screen)
		gridBox.addWidget(btn_cancel,9,1,1,1,Qt.Alignment(0))
		btn_apply=QPushButton(_("Save"))
		btn_apply.setIconSize(QSize(48,48))
		btn_apply.clicked.connect(self._save_desktop)
		gridBox.addWidget(btn_apply,9,2,1,1,Qt.Alignment(2))
		gui.setLayout(box)
		return(gui)
	#def _render_gui

	def _clear_screen(self):
		self.inp_name.setText("")
		self.inp_exec.setText("")
		self.inp_desc.setText("")
		self.gridBtnBox.clear()
		self.gridBtnBox.setRowCount(5)
		self.btn_categories={}
		self._set_categories()
		self.icon='exe'
		icn=QtGui.QIcon.fromTheme(self.icon)
		self.btn_icon.setIcon(icn)
	#def _clear_screen

	def _set_categories(self,loaded_categories=None):
		if not self.categories:
			self.categories=loaded_categories
		filter_categories=['debian','help','toys','kidsgames','action','control center','data management',\
						'file transfer','information','internet','communication','shells','translation',\
						'universal access','monitoring','package management','system','settingsmenu','screensavers',\
						'puzzles','lliurex preferences','look and feel','miscellaneous','preferences','network','audio',\
						'video','other','sound','administration','accessories','hardware','utilities','viewers',\
						'programming','applications','development','author tools','desktop','editors','graphics',\
						'chemistry','electronics','mathematics','science','lliurex administration']
		row=0
		col=0
		items_per_row=3
		self.categories.sort()
		for cat in self.categories:
			if cat and cat not in filter_categories:
				btn=QPushButton(cat)
				btn.setObjectName("btnCategory")
				btn.setCheckable(True)
				self.btn_categories[cat]=btn
				self.gridBtnBox.setCellWidget(row,col,btn)
				col+=1
				if not col%items_per_row:
					row+=1
					col=0
		self.gridBtnBox.resizeColumnsToContents()
		print("Grid Loaded")
	#def _set_categories
		
	def _load_desktop(self):
		fdesktop=self._file_chooser(path="/usr/share/applications")
		menu=App2Menu.app2menu()
		desktop=menu.get_desktop_info(fdesktop)
		if desktop:
			if desktop['NoDisplay']:
				self._show_message(_("Desktops with NoDisplay couldn't be loaded"))
			else:
				self.btn_categories={}
				self._clear_screen()
				self.inp_name.setText(desktop['Name'])
				self.inp_exec.setText(desktop['Exec'])
				self.inp_desc.setText(desktop['Comment'])
				sw_cat=False
				for cat in desktop['Categories']:
					if cat.lower() in self.btn_categories.keys():
						sw_cat=True
						self.btn_categories[cat.lower()].setChecked(True)
				if not sw_cat:
					lastCat=desktop['Categories'][-1]
					btn=QPushButton(lastCat.lower())
					btn.setObjectName("btnCategory")
					self.btn_categories[lastCat.lower()]=btn
					row=self.gridBtnBox.rowCount()
					self.gridBtnBox.insertRow(row)
					self.gridBtnBox.setCellWidget(row,0,btn)
					btn.setCheckable(True)
					btn.setChecked(True)
				if os.path.isfile(desktop['Icon']):
					icn=QtGui.QIcon(icon)
					pass
				else:
					icn=QtGui.QIcon.fromTheme(desktop['Icon'])
				self.btn_icon.setIcon(icn)
	#def _load_desktop
		
	def _save_desktop(self):
		categories=[]
		desktop={}
		for btnText,btn in self.btn_categories.items():
			if btn.isChecked():
				categories.append(btn.text())
		desktop['Name']=self.inp_name.text()
		desktop['Exec']=self.inp_exec.text()
		desktop['Icon']=self.icon
		desktop['Comment']=self.inp_desc.text()
		desktop['Categories']=';'.join(categories)
		self._debug("Saving %s"%desktop)
		try:
			subprocess.check_call(["pkexec","/usr/share/deskedit/bin/deskedit-helper.py",desktop['Name'],desktop['Icon'],desktop['Comment'],desktop['Categories'],desktop['Exec']])
			self._show_message(_("Added %s"%desktop['Name']),"background:blue")
		except:
			self._show_message(_("Error adding %s"%desktop['Name']))
	#def _save_desktop
	
	def _show_message(self,msg,css=None):
		def hide_message():
			timer=1000
			self.anim.setDuration(timer)
			self.anim.setStartValue(QRect(0,0,self.width()-10,self.height-10))
			self.anim.setEndValue(QRect(0,0,self.width()-10,0))
			self.anim.start()
			self.timer.singleShot(timer, lambda:self.statusBar.hide())
		if css:
				self.statusBar.setStyleSheet("""QStatusBar{color:white;%s;}"""%css)
		else:
				self.statusBar.setStyleSheet("""QStatusBar{background:red;color:white;}""")
		self.statusBar.showMessage("%s"%msg)
		self.anim.setDuration(1000)
		self.anim.setLoopCount(1)
		height=self.statusBar.height()/10
		if self.height<height:
			self.height=height
		self.statusBar.show()
		self.anim.setStartValue(QRect(0,0,self.width()-10,0))
		self.anim.setEndValue(QRect(0,0,self.width()-10,self.height-10))
		self.anim.start()
		self.timer.singleShot(3000, lambda:hide_message())

	def _set_css(self):
			css="""
	
			#btnCategory{
				color:grey;
				border-width:3px;
				background:white;
				border-style:groove;
				padding:3px;
			}

			#btnCategory:checked{
				color:black;
				font-style:bold;
				background:silver;
				border-style:ridge;
				border-color:grey;
			}

			#btnIcon{
				border:0px;
				margin:0px;
				padding:0px;
			}

			#btnFile{
				padding:3px;
				padding-left:6px;
				padding-right:6px;
			}

			QLabel{
				font:12px Roboto;
				margin:0px;
				border:0px;
				padding:3px;
			}

			QLineEdit{
				border:0px;
				border-bottom:1px solid grey;
				padding:1px;
				font:14px Roboto;
				margin-right:6px;
			}

			
			"""
			return(css)



app=QApplication([])
editor=desktopEditor()
app.exec_()
