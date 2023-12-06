import sys

from PyQt5 import QtCore, QtGui, QtWidgets

import cut
import choose

from choose import UI as A_Ui  # a界面的库
from cut import UI as B_Ui  # b界面的库

from PyQt5 import QtCore, QtWidgets
import sys
import config


# self.actionzh.setText(_translate("MainWindow", "中文"))
# self.actionen.setText(_translate("MainWindow", "English"))
# self.actionFranch.setText(_translate("MainWindow", "Français"))
# self.actionGerman.setText(_translate("MainWindow", "Deutsch"))
# self.actionJapenese.setText(_translate("MainWindow", "日本語"))
# self.actionalabo.setText(_translate("MainWindow", "اللغة العربية"))
# self.actionlading.setText(_translate("MainWindow", "Lingua Latīna"))
# self.actionxibolai.setText(_translate("MainWindow", "עִבְרִית"))
# self.actionselect.setText(_translate("MainWindow", "步骤二 选区"))
# self.actioncut.setText(_translate("MainWindow", "步骤一 裁剪"))

def setConnectui(ui1, ui2):
    # ui1.actionzh.triggered.connect(ui.network)
    # ui1.actionen.triggered.connect(ui.network)
    # ui1.actionFranch.triggered.connect(ui.network)
    # ui1.actionGerman.triggered.connect(ui.network)
    # ui1.actionJapenese.triggered.connect(ui.network)
    # ui1.actionalabo.triggered.connect(ui.network)
    # ui1.actionlading.triggered.connect(ui.network)
    # ui1.actionxibolai.triggered.connect(ui.network)

    ui1.actionselect.triggered.connect(
        lambda: {ui1.close(), ui2.changeLanguage(config.now_Lan), ui2.show(), ui2.showMaximized()})
    ui1.actioncut.triggered.connect(
        lambda: {ui2.close(), ui1.changeLanguage(config.now_Lan), ui1.show(), ui1.showMaximized()})

    # ui2.actionzh.triggered.connect(ui.network)
    # ui2.actionen.triggered.connect(ui.network)
    # ui2.actionFranch.triggered.connect(ui.network)
    # ui2.actionGerman.triggered.connect(ui.network)
    # ui2.actionJapenese.triggered.connect(ui.network)
    # ui2.actionalabo.triggered.connect(ui.network)
    # ui2.actionlading.triggered.connect(ui.network)
    # ui2.actionxibolai.triggered.connect(ui.network)

    ui2.actionselect.triggered.connect(
        lambda: {ui1.close(), ui2.changeLanguage(config.now_Lan), ui2.show(), ui2.showMaximized()})
    ui2.actioncut.triggered.connect(
        lambda: {ui2.close(), ui1.changeLanguage(config.now_Lan), ui1.show(), ui1.showMaximized()})


def changeUI(ui1):
    ui1.show()


class AUi(QtWidgets.QMainWindow, A_Ui):
    def __init__(self):
        super(AUi, self).__init__()
        self.setupUi(self)


class BUi(QtWidgets.QMainWindow, B_Ui):
    def __init__(self):
        super(BUi, self).__init__()
        self.setupUi(self)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    a = BUi()
    b = AUi()
    a.showMaximized()
    setConnectui(a, b)
    config.now_Lan = config.Language.Eng
    a.actioncut.trigger()
    sys.exit(app.exec_())
