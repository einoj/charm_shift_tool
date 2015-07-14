import sys
#from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QMainWindow, QApplication
from cst import Ui_MainWindow

class Window(QMainWindow, Ui_MainWindow):
  def __init__(self, parent = None):

    QMainWindow.__init__(self, parent)

    self.setupUi(self)

if __name__ == '__main__':
  cst = QApplication(sys.argv)
  window = Window()

  window.show()
  #appLabel = QQuickView()
  #appLabel.setSource(QUrl('cst.qml'))

  #appLabel.show()

  #cst.exec_()
  sys.exit(cst.exec_())

