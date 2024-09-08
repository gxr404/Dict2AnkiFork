try:
  from aqt import mw
  from .addon.addonWindow import Windows
  from PyQt6.QtGui import QAction

  def showWindow():
    w = Windows()
    w.exec()

  action = QAction("Dict2Anki...", mw)
  action.triggered.connect(showWindow)
  mw.form.menuTools.addAction(action)

except ImportError:
  import os
  import sys
  from PyQt6.QtWidgets import QApplication
  from addon.addonWindow import Windows

  # TODO: to be deleted test 环境
  # os.environ['DEVDICT2ANKI']= "1"
  if os.environ.get('DEVDICT2ANKI'):
    app = QApplication(sys.argv)
    window = Windows()
    window.show()
    sys.exit(app.exec())
