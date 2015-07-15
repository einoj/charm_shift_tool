import sys
#from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QMainWindow, QApplication
from cst import Ui_MainWindow

class GUI(QMainWindow, Ui_MainWindow):
  def __init__(self, parent = None):

    QMainWindow.__init__(self, parent)

    self.setupUi(self)

  def updateMsg(self, msg):
    _translate = QCoreApplication.translate
    self.plainTextEdit.setPlainText(_translate("MainWindow", msg))

if __name__ == '__main__':
  cst = QApplication(sys.argv)
  window = GUI()

  window.show()
  window.updateMsg("Hallo")
  #appLabel = QQuickView()
  #appLabel.setSource(QUrl('cst.qml'))

  #appLabel.show()

  #cst.exec_()
  sys.exit(cst.exec_())

