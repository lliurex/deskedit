#!/usr/bin/env python3
import sys
import os
from app2menu import App2Menu
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QVBoxLayout,\
				QDialog,QStackedWidget,QGridLayout,QTabWidget,QHBoxLayout,QFormLayout,QLineEdit,QComboBox,\
				QStatusBar,QFileDialog,QDialogButtonBox,QScrollBar,QScrollArea,QCheckBox,QTableWidget,\
				QTableWidgetItem,QHeaderView,QTableWidgetSelectionRange
from PyQt5 import QtGui
from PyQt5.QtCore import QSize,pyqtSlot,Qt, QPropertyAnimation,QThread,QRect,QTimer,pyqtSignal,QSignalMapper
import gettext

class desktopEditor(QWidget):

	def __init__(self):
		super().__init__()
		self.dbg=False
		self.desktop={'icon':'x-appimage','name':'','comment':'','categories':'Utility'}
#		self._render_gui(desktop)

	def _read_desktop_file(self,desktop_file):
		menu=App2Menu.app2menu()
		self.desktop=menu.get_desktop_info(desktop_file)

	#def _set_desktop_info
	
	def _dbg(self,msg):
		if self.dbg:
			print("DeskEdit: %s"%msg)

	def _render_gui(self):
		box=QGridLayout()
		categories=[]
		fdia=QFileDialog()
		icon="x-appimage"
		def _file_chooser():
			fdia.setFileMode(QFileDialog.AnyFile)
			fdia.setNameFilter(_("images(*.png *.xpm *jpg)"))
			if (fdia.exec_()):
				icon=fdia.selectedFiles()[0]
				icn=QtGui.QIcon(icon)
				btn_icon.setIcon(icn)

		def _begin_save_desktop():
			name=inp_name.text()
			comment=inp_desc.text()
			categories=cmb_cat.currentText()
			desktop['name']=name
			if fdia.selectedFiles():
				icon=fdia.selectedFiles()[0]
			else:
				icon='x-appimage'
			desktop['icon']=icon
			desktop['comment']=comment
			desktop['categories']=categories
#			dia.accept()
			
		def _set_categories(categories):
			filter_categories=['debian','help']
			for cat in categories:
				if cat and cat not in filter_categories:
					cmb_cat.addItem(_(cat))
			cmb_cat.adjustSize()
		dia=QDialog()
		dia.setWindowTitle("Appimage Desktop Definition")
		box=QFormLayout()
		lbl_icon=QLabel(_("Select icon: "))
		inp_icon=QLineEdit(desktop['icon'])
		btn_icon=QPushButton()
		icn_desktop=QtGui.QIcon.fromTheme(icon)
		btn_icon.setIcon(icn_desktop)
		btn_icon.setIconSize(QSize(64,64))
		btn_icon.clicked.connect(_file_chooser)
		box.addRow(lbl_icon,btn_icon)
		lbl_name=QLabel(_("Set name: "))
		inp_name=QLineEdit(desktop['name'])
		box.addRow(lbl_name,inp_name)
		lbl_desc=QLabel(_("Set desc: "))
		inp_desc=QLineEdit(desktop['comment'])
		box.addRow(lbl_desc,inp_desc)
		lbl_cat=QLabel(_("Set category: "))
		cmb_cat=QComboBox()
		cmb_cat.setSizeAdjustPolicy(0)
		th_categories=th_getCategories()
		th_categories.start()
		th_categories.signal.connect(_set_categories)
		box.addRow(lbl_cat,cmb_cat)
		btnBox=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
		btnBox.rejected.connect(dia.reject)
		btnBox.accepted.connect(_begin_save_desktop)
#		box.addRow(btn_apply,btn_cancel)
		box.addRow(btnBox)
		dia.setLayout(box)
#		dia.show()
#		result=dia.exec_()
#		return (desktop,result==QDialog.Accepted)
	#def _render_desktop_dialog


app=QApplication([])
editor=desktopEditor()
app.exec_()
