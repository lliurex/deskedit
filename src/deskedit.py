#!/usr/bin/env python3
import sys
import os
from app2menu import App2Menu
from PySide2.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QGridLayout,\
				QHBoxLayout,QLineEdit,QFileDialog,QTableWidget,QToolBar
from PySide2 import QtGui
from PySide2.QtCore import QSize,Qt, QThread,Signal
import gettext
import subprocess
gettext.textdomain('deskedit')
_ = gettext.gettext

RSRC="/usr/share/deskedit/rsrc"

i18n={"ADD_NEW":_("Add a new app launcher"),
	"ADDED":_("Added"),
	"ALL_FILES":_("All files(*.*)"),
	"BTN_TOOLTIP":_("Push to change icon"),
	"BTNEXEC_TOOLTIP":_("Press button to select an executable"),
	"CATEGORIES":_("Categories: "),
	"DESCRIPTION":_("Description: "),
	"DESCRIPTION_TOOLTIP":_("Insert a description for the app"),
	"ERR_ADD":_("Error adding"),
	"ERR_NODISPLAY":_("Desktops with NoDisplay couldn't be loaded"),
	"EXEC":_("Executable: "),
	"EXEC_PATH":_("Executable path"),
	"EXEC_TOOLTIP":_("Insert path to the executable"),
	"IMAGES":_("Images"),
	"LOAD":_("Load a desktop file from system"),
	"NAME":_("Name: "),
	"NAME_DESKTOP":_("Desktop name"),
	"NAME_INSERT":_("Insert desktop name"),
	"SAVE":_("Save"),
	"SAVE_DESKTOP":_("Save desktop"),
	"TITLE":_("Desktop Editor")
	}
class th_getCategories(QThread):
	endProcess=Signal("PyObject")
	def __init__(self):
		QThread.__init__(self)
	#def __init__

	#def __del__(self):
	#	self.wait()

	def run(self):
		menu=App2Menu.app2menu()
		categories=menu.get_categories()
		self.endProcess.emit(categories)
	#def run
#class th_getCategories

class desktopEditor(QWidget):

	def __init__(self,desktop_file=None):
		super().__init__()
		QtGui.QGuiApplication.setDesktopFileName("deskedit")
		self.setWindowIcon(QtGui.QIcon.fromTheme("deskedit"))
		self.setObjectName("mainWindow")
		self.dbg=False
		self._debug("Rendering gui...")
		self.categories=[]
		self.categories_translator={}
		self.icon=os.path.join(RSRC,"/exec.png")
		self.filename=''
		desktop=self._readDesktopFile(desktop_file)
		box=QGridLayout()
		img_banner=QLabel()
		img=QtGui.QPixmap(os.path.join(RSRC,"/deskedit_banner.png"))
		img_banner.setPixmap(img)
		box.addWidget(img_banner,0,0,1,1)
		box.addWidget(self._renderGui(desktop),1,0,1,1)
		self.setStyleSheet(self._setCss())
		self.setLayout(box)
		self.show()
	#def __init__
	
	def _debug(self,msg):
		if self.dbg:
			print("DeskEdit: {}".format(msg))
	#def _debug
	
	def _readDesktopFile(self,desktop_file=None):
		menu=App2Menu.app2menu()
		if desktop_file:
			desktop=menu.get_desktop_info(desktop_file)
		else:
			desktop=menu.init_desktop_file()
		return(desktop)
	#def _readDesktopFile

	def _fileChooser(self,widget=None,path=None,imgDialog=None):
		fdia=QFileDialog()
		fchoosed=''
		fdia.setFileMode(QFileDialog.AnyFile)
		if imgDialog:
			fdia.setNameFilter(_("images(*.png *.xpm *jpg)"))
			fdia.setNameFilter("{} (*.png *.xpm *jpg)".format(i18n["IMAGES"]))
		else:
			fdia.setNameFilter(i18n["ALL_FILES"])
		if path:
			self._debug("Set path to {}".format(path))
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

	def _renderGui(self,desktop):
		categories=[]
		gui=QWidget()
		gui.setWindowTitle(i18n["TITLE"])
		box=QHBoxLayout()
		self.btn_categories={}
		gridBox=QGridLayout()
		self.gridBtnBox=QTableWidget(5,3)
		self.gridBtnBox.horizontalHeader().hide()
		self.gridBtnBox.verticalHeader().hide()
		self.gridBtnBox.setShowGrid(False)
		self.gridBtnBox.setEditTriggers(QTableWidget.NoEditTriggers)
		box.addLayout(gridBox)
		tlb_controls=QToolBar()
		gridBox.addWidget(tlb_controls,0,0,1,3)
		icn_new=QtGui.QIcon.fromTheme("list-add")
		tlb_controls.addAction(icn_new,i18n["ADD_NEW"],self._resetScreen)
		icn_load=QtGui.QIcon.fromTheme("document-open")
		tlb_controls.addAction(icn_load,i18n["LOAD"],self._loadDesktopFile)


		lbl_icon=QLabel(_("Icon: "))
		gridBox.addWidget(lbl_icon,1,2,1,1)
		self.btn_icon=QPushButton()
		self.btn_icon.setObjectName("btnIcon")
		icn_desktop=QtGui.QIcon.fromTheme(self.icon)
		self.btn_icon.setIcon(icn_desktop)
		self.btn_icon.setIconSize(QSize(64,64))
		self.btn_icon.setToolTip(i18n["BTN_TOOLTIP"])
		self.btn_icon.clicked.connect(lambda:self._fileChooser(widget=self.btn_icon,imgDialog=True))
		gridBox.addWidget(self.btn_icon,2,2,3,1)
		lbl_name=QLabel(i18n["NAME"])
		gridBox.addWidget(lbl_name,1,0,1,2)
		self.inp_name=QLineEdit(desktop['Name'])
		self.inp_name.setPlaceholderText(i18n["NAME_DESKTOP"])
		self.inp_name.setToolTip(i18n["NAME_INSERT"])
		gridBox.addWidget(self.inp_name,2,0,1,2)
		lbl_exec=QLabel(i18n["EXEC"])
		gridBox.addWidget(lbl_exec,3,0,1,2)
		self.inp_exec=QLineEdit(desktop['Exec'])
		self.inp_exec.setPlaceholderText(i18n["EXEC_PATH"])
		self.inp_exec.setToolTip(i18n["EXEC_TOOLTIP"])
		gridBox.addWidget(self.inp_exec,4,0,1,1,Qt.Alignment(0))
		btn_exec=QPushButton("...")
		btn_exec.setObjectName("btnFile")
		btn_exec.setToolTip(i18n["BTNEXEC_TOOLTIP"])
		btn_exec.clicked.connect(lambda:self._fileChooser(widget=self.inp_exec))
		gridBox.addWidget(btn_exec,4,1,1,1,Qt.Alignment(1))
		lbl_desc=QLabel(i18n["DESCRIPTION"])
		gridBox.addWidget(lbl_desc,5,0,1,2)
		self.inp_desc=QLineEdit(desktop['Comment'])
		self.inp_desc.setPlaceholderText(i18n["DESCRIPTION"])
		self.inp_desc.setToolTip(i18n["DESCRIPTION_TOOLTIP"])
		gridBox.addWidget(self.inp_desc,6,0,1,3)
		lbl_cat=QLabel(i18n["CATEGORIES"])
		gridBox.addWidget(lbl_cat,7,0,1,2)
		gridBox.addWidget(self.gridBtnBox,8,0,1,3)
		self.th_categories=th_getCategories()
		self.th_categories.endProcess.connect(self.setCategories)
		self.th_categories.start()
		btn_apply=QPushButton(i18n["SAVE"])
		btn_apply.setToolTip(i18n["SAVE_DESKTOP"])
		btn_apply.setIconSize(QSize(48,48))
		btn_apply.clicked.connect(self._saveDesktopFile)
		gridBox.addWidget(btn_apply,9,2,1,1,Qt.Alignment(2))
		gui.setLayout(box)
		return(gui)
	#def _renderGui

	def _resetScreen(self):
		self.inp_name.setText("")
		self.inp_exec.setText("")
		self.inp_desc.setText("")
		self.gridBtnBox.clear()
		self.gridBtnBox.setRowCount(5)
		self.btn_categories={}
		self.setCategories()
		self.icon=os.path.join(RSRC,'exec.png')
		icn=QtGui.QIcon.fromTheme(self.icon)
		self.btn_icon.setIcon(icn)
		self.filename=''
	#def _resetScreen

	def setCategories(self,loaded_categories=None):
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
		self.categories_translator['multimedia']="AudioVideo;Graphics"
		self.categories_translator['games']="Game"
		self.categories_translator['internet and network']="Internet"
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
	#def setCategories
		
	def _loadDesktopFile(self):
		fdesktop=self._fileChooser(path="/usr/share/applications")
		menu=App2Menu.app2menu()
		desktop={}
		if fdesktop:
			desktop=menu.get_desktop_info(fdesktop)
		if desktop:
			if desktop['NoDisplay']:
				self._showMsg(i18n["ERR_NODISPLAY"])
			else:
				self._resetScreen()
				self.filename=fdesktop
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
				self.icon=desktop['Icon']
				if os.path.isfile(desktop['Icon']):
					icn=QtGui.QIcon(desktop['Icon'])
					pass
				else:
					icn=QtGui.QIcon.fromTheme(desktop['Icon'])
				self.btn_icon.setIcon(icn)
	#def _loadDesktopFile
		
	def _saveDesktopFile(self):
		categories=[]
		desktop={}
		for btnText,btn in self.btn_categories.items():
			if btn.isChecked():
				categories.append(btn.text().capitalize())
		desktop['Name']=self.inp_name.text()
		desktop['Exec']=self.inp_exec.text()
		desktop['Icon']=self.icon
		desktop['Comment']=self.inp_desc.text()
		tmp_cat=[]
		for cat in categories:
			if cat.lower() in self.categories_translator.keys():
				tmp_cat.append(self.categories_translator[cat.lower()])
			else:
				tmp_cat.append(cat)
		desktop['Categories']=';'.join(tmp_cat)
		self._debug("Saving %s"%desktop)
		self._debug("filename %s"%self.filename)
		self.filename=desktop['Name']
		self.filename=self.filename.replace(" ","").lower().replace(".","").replace("-","")
		self.filename="net.deskedit.{0}.desktop".format(self.filename)
		self.filepath=os.path.join("/tmp",self.filename)
		self.writeTmpDesktop(desktop)
		try:
			#subprocess.check_call(["pkexec","/usr/share/app2menu/app2menu-helper.py",desktop['Name'],desktop['Icon'],desktop['Comment'],desktop['Categories'],desktop['Exec'],self.filename])
			destdir=os.path.join(os.environ["HOME"],".local","share","applications")
			if os.path.exists(destdir)==False:
				os.makedirs(destdir)
			subprocess.check_call(["desktop-file-install","--vendor=net.deskedit","--dir={}".format(destdir),self.filepath])
		except:
			self._showMsg("{0} {1}".format(i18n["ERR_ADD"],desktop['Name']))
		else:
			self._showMsg("{0} {1}\n({2})".format(i18n["ADDED"],desktop['Name'],self.filepath),"success")
	#def _saveDesktopFile

	def writeTmpDesktop(self,desktop):
		fname=os.path.basename(self.filename)
		content=["[Desktop Entry]\n",
				"Version=1.0\n",
				"Encoding=UTF-8\n",
				"Type=Application\n"]
		for key,value in desktop.items():
			content.append("{0} = {1}\n".format(key,value))
		with open(os.path.join("/tmp/",fname),"w") as f:
			f.writelines(content)
	#def writeTmpDesktop

	def _showMsg(self,msg,status=None):
		#self.statusBar.setText(msg)
		#if status:
		#	self.statusBar.show(status)
		#else:
		#	self.statusBar.show()
		subprocess.run(["notify-send","-u","normal","-t","5000","-a","DeskEdit","-i","deskedit","-e","DeskEdit",msg])
		return

	def _setCss(self):
			css="""
			#mainWindow{
				padding:0px;
				margin:0px;
				border:0px;
			}

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
				border:1px solid silver;
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

			QTableWidget{
				background:rgba(255,255,255,0);
			}
			
			"""
			return(css)



app=QApplication(["DeskEdit"])
editor=desktopEditor()
app.exec_()
