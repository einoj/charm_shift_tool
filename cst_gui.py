import sys
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication
from PyQt5.QtQuick import QQuickView

if __name__ == '__main__':
  cst = QApplication(sys.argv)
  appLabel = QQuickView()
  appLabel.setSource(QUrl('cst.qml'))

  appLabel.show()

  cst.exec_()
  sys.exit()
