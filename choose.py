import csv
from copy import deepcopy
from xml.dom import minidom
import os
import numpy
import sys

import config
from config import Language

from PIL import Image, ImageQt

from PyQt5.Qt import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from numpy import *
from copy import deepcopy

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QPolygon
import cut


class ImageBox(QWidget):
    def __init__(self, lineEdit_B, lineEdit_G, lineEdit_R, lineEdit_pensize, lineEdit_magic):
        super(ImageBox, self).__init__()

        self.selectMinusOrPlus = 1
        self.lineEdit_B = lineEdit_B
        self.lineEdit_G = lineEdit_G
        self.lineEdit_R = lineEdit_R
        self.lineEdit_pensize = lineEdit_pensize
        self.lineEdit_magic = lineEdit_magic

        self.img_array = None

        self.right_click = None
        self.zoom = 1

        self.pointPaint = None
        self.move_flag = None
        self.img = None
        self.scaled_img = None
        self.select_img = None
        self.select_img_before = None

        self.point = QPoint(0, 0)
        self.start_pos = None
        self.end_pos = None
        self.left_click = False
        self.scale = 1
        self.points = []
        self.setFocus()
        self.setFocusPolicy(Qt.StrongFocus)
        self.rectOp = False
        self.MagicOp = False
        self.PolygonOp = False
        self.showSelect = False

        self.edit = True
        self.polyList = []
        self.diff = 15
        self.pensize = 10
        self.im = Image
        self.Qrgb = qRgb(0, 0, 0)
        self.arraylist = None
        self.arraylist_before = None

    def save(self):
        self.select_img_before = self.select_img.copy()
        self.arraylist_before = deepcopy(self.arraylist)

    def cancel(self):
        self.select_img = self.select_img_before
        self.arraylist = self.arraylist_before
        self.repaint()

    def paintSelect(self):
        self.save()
        self.Qrgb = qRgb(int(self.lineEdit_R.text()), int(self.lineEdit_G.text()), int(self.lineEdit_B.text()))
        self.select_img = self.img.copy()
        qimage = QtGui.QImage(self.select_img)
        for i in range(0, self.arraylist.shape[0]):
            for j in range(0, self.arraylist.shape[1]):
                if self.arraylist[i][j] == 1:
                    qimage.setPixel(i, j, self.Qrgb)
        self.select_img = QtGui.QPixmap(qimage)

    def rectOperation(self, x, y):
        self.save()
        self.Qrgb = qRgb(int(self.lineEdit_R.text()), int(self.lineEdit_G.text()), int(self.lineEdit_B.text()))
        qimage = QtGui.QImage(self.select_img)
        for i in range(int(x - float(self.lineEdit_pensize.text()) / self.scale / 2.0),
                       int(x + float(self.lineEdit_pensize.text()) / self.scale / 2.0)):
            for j in range(int(y - float(self.lineEdit_pensize.text()) / self.scale / 2.0),
                           int(y + float(self.lineEdit_pensize.text()) / self.scale / 2.0)):
                self.arraylist[i][j] = self.selectMinusOrPlus
                if (self.selectMinusOrPlus):
                    qimage.setPixel(i, j, self.Qrgb)
                else:
                    qimage.setPixel(i, j, self.qRgb(self.img_array[j, i][0], self.img_array[j, i][1],
                                                    self.img_array[j, i][2]))
        self.select_img = QtGui.QPixmap(qimage)

    def magicOperation(self, x, y):
        self.save()
        self.Qrgb = qRgb(int(self.lineEdit_R.text()), int(self.lineEdit_G.text()), int(self.lineEdit_B.text()))
        qimage = QtGui.QImage(self.select_img)
        x = int(x)
        y = int(y)
        for i in range(0, self.img_array.shape[0]):
            for j in range(0, self.arraylist.shape[1]):
                op2 = sqrt(1.0 * (self.img_array[j, i][0] - self.img_array[y, x][0]) ** 2 +
                           1.0 * (self.img_array[j, i][1] - self.img_array[y, x][1]) ** 2 +
                           1.0 * (self.img_array[j, i][2] - self.img_array[y, x][2]) ** 2)
                if op2 < int(self.lineEdit_magic.text()):
                    self.arraylist[i][j] = self.selectMinusOrPlus
                    if (self.selectMinusOrPlus):
                        qimage.setPixel(i, j, self.Qrgb)
                    else:
                        qimage.setPixel(i, j, self.qRgb(self.img_array[j, i][0], self.img_array[j, i][1],
                                                        self.img_array[j, i][2]))
        self.select_img = QtGui.QPixmap(qimage)

    def polygonOperation(self, rectx):

        self.save()
        self.Qrgb = qRgb(int(self.lineEdit_R.text()), int(self.lineEdit_G.text()), int(self.lineEdit_B.text()))
        qimage = QtGui.QImage(self.select_img)
        qp = QPolygon(QRect(0, 0, self.img.width(), self.img.height()))
        qp = qp.intersected(rectx)
        for i in range(0, self.arraylist.shape[0]):
            for j in range(0, self.arraylist.shape[1]):
                if qp.containsPoint(QPoint(i, j), Qt.FillRule.OddEvenFill):
                    self.arraylist[i][j] = self.selectMinusOrPlus
                    if (self.selectMinusOrPlus):
                        qimage.setPixel(i, j, self.Qrgb)
                    else:
                        qimage.setPixel(i, j, qRgb(self.img_array[j, i][0], self.img_array[j, i][1],
                                                   self.img_array[j, i][2]))

        self.select_img = QtGui.QPixmap(qimage)

    def init_ui(self):
        self.setWindowTitle("ImageBox")

    def set_image(self, img_path):
        """
        open image file
        :param img_path: image file path
        :return:
        """

        path = img_path
        self.path = ""
        path = path.split("/", -1)
        for i in range(0, len(path) - 1):
            self.path += (path[i] + "/")

        print(self.path)
        x = Image.open(img_path)
        self.img_array = numpy.asarray(x)
        self.img = QPixmap(img_path)
        self.scaled_img = self.img
        self.select_img = self.img
        self.arraylist = numpy.zeros((self.img.width(), self.img.height()))

    def paintEvent(self, e):
        """
        receive paint events
        :param e: QPaintEvent
        :return:
        """
        if self.showSelect:
            painter = QPainter()
            painter.begin(self)
            painter.scale(self.scale, self.scale)
            painter.drawPixmap(self.point, self.select_img)
            painter.end()
        elif self.scaled_img:
            painter = QPainter()
            painter.begin(self)
            painter.scale(self.scale, self.scale)
            painter.drawPixmap(self.point, self.scaled_img)
            painter.end()

        if len(self.polyList) != 0 and self.PolygonOp:
            painter = QPainter()
            painter.begin(self)
            painter.scale(self.scale, self.scale)
            painter.setPen(QPen(Qt.red, 5))  # 画点，红色
            for k in range(len(self.polyList)):
                painter.drawPoint(self.point + self.polyList[k])
            if (len(self.polyList) > 1):
                painter.setPen(QPen(Qt.blue, 4, Qt.SolidLine))
                for i in range(1, len(self.polyList)):
                    painter.drawLine(self.point + self.polyList[i - 1], self.point + self.polyList[i])
        """if self.pointPaint:
            super().paintEvent(e)
            painter = QPainter()
            painter.begin(self)
            painter.setPen(QPen(Qt.blue, 4, Qt.SolidLine))  # 实线画笔，蓝色
            if len(self.points) == 2:
                painter.drawLine(self.points[0][0], self.points[0][1], self.points[1][0], self.points[1][1])
            painter.setPen(QPen(Qt.red, 10))  # 画点，红色
            for k in range(len(self.points)):
                painter.drawPoint(self.points[k][0], self.points[k][1])
            painter.end()"""

    def wheelEvent(self, event):
        angle = event.angleDelta() / 8  # 返回QPoint对象，为滚轮转过的数值，单位为1/8度
        angleY = angle.y()
        # 获取当前鼠标相对于view的位置
        if angleY > 0:
            self.scale *= 1.1
        else:  # 滚轮下滚
            self.scale *= 0.9
        self.adjustSize()
        self.update()

    def mouseMoveEvent(self, e):
        """
        mouse move events for the widget
        :param e: QMouseEvent
        :return:
        """

        if self.left_click and self.move_flag:
            self.end_pos = e.pos() - self.start_pos
            self.point = self.point + self.end_pos
            self.start_pos = e.pos()
            self.repaint()

    def mousePressEvent(self, e):
        """
        mouse press events for the widget
        :param e: QMouseEvent
        :return:
        """
        if e.buttons() == Qt.LeftButton and self.move_flag:
            self.left_click = True
            self.start_pos = e.pos()
        elif self.MagicOp and e.buttons() == Qt.LeftButton and self.edit:
            self.magicOperation(e.pos().x() / self.scale - self.point.x(), e.pos().y() / self.scale - self.point.y())
            self.repaint()
        elif self.rectOp and e.buttons() == Qt.LeftButton and self.edit:
            self.rectOperation(e.pos().x() / self.scale - self.point.x(), e.pos().y() / self.scale - self.point.y())
            self.repaint()
        elif self.PolygonOp and e.buttons() == Qt.LeftButton and self.edit:
            self.polyList.append(e.pos() / self.scale - self.point)
            self.repaint()
        elif self.PolygonOp and e.buttons() == Qt.RightButton and self.edit:
            qp = QPolygon(self.polyList)
            self.polygonOperation(qp)
            self.polyList = []
            self.repaint()

        elif e.buttons() == Qt.LeftButton:  # 左键点击
            if not self.move_flag:
                if len(self.points) == 2:
                    self.points.clear()  # 清空绝对坐标
                x0 = e.x()
                y0 = e.y()
                self.points.append([x0, y0])
                self.update()  # 获取鼠标点击的点之后，通知画线
        elif e.buttons() == Qt.RightButton:  # 右键点击
            self.right_click = True

    def mouseReleaseEvent(self, e):
        """
        mouse release events for the widget
        :param e: QMouseEvent
        :return:
        """
        if e.button() == Qt.LeftButton:
            self.left_click = False

    def getGlobalPos(self):  # 返回绝对坐标
        return self.points

    def keyPressEvent(self, ev):
        if ev.key() == Qt.Key_W:
            self.move_flag = True
        elif ev.key() == Qt.Key_D:
            self.pointPaint = True
        elif ev.key() == Qt.Key_P:
            for i in range(0, self.img.width()):
                for j in range(0, self.img.height()):
                    self.arraylist[i][j] = not self.arraylist[i][j]
            self.paintSelect()
        elif ev.key() == Qt.Key_Escape:
            self.cancellAll()
        elif ev.key() == Qt.Key_O:
            self.finish()

    def cancellAll(self):
        for i in range(0, self.img.width()):
            for j in range(0, self.img.height()):
                self.arraylist[i][j] = 0
        self.paintSelect()
        self.repaint()

    def svgfinish(self):
        self.svgConsole(self.arraylist)

    def listFinish(self):
        self.listConsole(self.arraylist)

    def svgConsole(self, arg):
        # hostdev1 = dom.getElementsByTagName("hostdev")  # hostdev1是标签为hostdev的节点列表
        # hostdev1[0].parentNode.removeChild(hostdev1[0])  # 删除节点得从其父节点删除子节点
        #
        # fp = open(xml_path, 'w', encoding='utf-8')
        # dom.writexml(fp, indent='', addindent='', newl='', encoding='utf-8')
        # fp.close()
        img_name, _ = QFileDialog.getOpenFileName(None, "Open Image File", "", "*.svg")
        if img_name != "":
            domobj = minidom.parse(img_name)
            rooty = domobj.documentElement
            root = rooty.getElementsByTagName("rect")
            width = float(root[2].getAttribute("width"))

            for j in range(1, len(root)):
                element = root[j]
                x = (float(root[j].getAttribute("x")) - float(root[0].getAttribute("x")))  # / width
                y = (float(root[j].getAttribute("y")) - float(root[0].getAttribute("y")))  # / width
                x = int(round(x))
                y = int(round(y))
                x2 = int(x + width)
                y2 = int(y + width)
                num = 0
                for i in range(x, x2):
                    for j2 in range(y, y2):
                        num += arg[i][j2]
                if num <= width * width / 2:
                    root[j].parentNode.removeChild(root[j])

            path = self.path + "test.svg"
            fp = open(path, 'w', encoding='utf-8')
            domobj.writexml(fp, indent='', addindent='', newl='', encoding='utf-8')
            fp.close()

    def listConsole(self, arg):
        # hostdev1 = dom.getElementsByTagName("hostdev")  # hostdev1是标签为hostdev的节点列表
        # hostdev1[0].parentNode.removeChild(hostdev1[0])  # 删除节点得从其父节点删除子节点
        #
        # fp = open(xml_path, 'w', encoding='utf-8')
        # dom.writexml(fp, indent='', addindent='', newl='', encoding='utf-8')
        # fp.close()

        a = numpy.zeros(shape=(4900, 6)).astype(numpy.object_)
        with open('barcode.txt', 'r', encoding='utf-8') as f:
            for i in range(0, 4900):
                a[i][0] = f.readline().strip("\n")

        for i in range(1, 71):
            for j in range(1, 71):
                x = (i - 1) * 3 + i * 5
                y = (j - 1) * 3 + j * 5
                a[(i - 1) * 70 + j - 1][2] = str(i)
                a[(i - 1) * 70 + j - 1][3] = str(j)
                a[(i - 1) * 70 + j - 1][4] = str(x)
                a[(i - 1) * 70 + j - 1][5] = str(y)
                a[(i - 1) * 70 + j - 1][1] = "0"
                for x1 in range(x - 5, x):
                    for y1 in range(556 - y, 561 - y):
                        if arg[y1][x1] == 1:
                            a[(i - 1) * 70 + j - 1][1] = "1"

        with open(self.path + 'file.tsv', 'w', newline='') as f:
            tsv_w = csv.writer(f, delimiter='\t')
            tsv_w.writerows(a.tolist())  # 多行写入

    def keyReleaseEvent(self, a0: QKeyEvent):
        if a0.key() == Qt.Key_W:
            self.move_flag = False
        elif a0.key() == Qt.Key_D:
            self.pointPaint = False


class UI(object):
    def __init__(self):
        self.translator = QTranslator()
        self.cancelAllButton = QtWidgets.QPushButton()
        self.flushButton = QtWidgets.QPushButton()
        self.cancelButton = QtWidgets.QPushButton()
        self.finishButton = QtWidgets.QPushButton()
        self.colorLabel = QtWidgets.QLabel()

        self.s1 = QScrollBar()
        self.img = QImage()
        self.actImg = QImage()
        self.arraylist = numpy.zeros((5, 5))
        self.Qrgb = qRgb
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollArea = QtWidgets.QScrollArea()
        self.lineEdit_B = QtWidgets.QLineEdit()
        self.lineEdit_G = QtWidgets.QLineEdit()
        self.lineEdit_R = QtWidgets.QLineEdit()
        self.lineEdit_pensize = QtWidgets.QLineEdit()
        self.lineEdit_magic = QtWidgets.QLineEdit()
        self.penButton = QtWidgets.QPushButton()
        self.openFileButton = QtWidgets.QPushButton()
        self.rectButton = QtWidgets.QPushButton()
        self.showButton = QtWidgets.QPushButton()
        self.magicButton = QtWidgets.QPushButton()
        self.editButton = QtWidgets.QPushButton()
        self.box = ImageBox(self.lineEdit_B,
                            self.lineEdit_G,
                            self.lineEdit_R,
                            self.lineEdit_pensize,
                            self.lineEdit_magic)

    def setconnected(self):
        self.lineEdit_B.setText(str(0))
        self.lineEdit_G.setText(str(0))
        self.lineEdit_R.setText(str(0))
        self.lineEdit_pensize.setText(str(10))
        self.lineEdit_magic.setText(str(100))

        self.openFileButton.clicked.connect(self.open_image)
        self.penButton.clicked.connect(self.setpen)
        self.rectButton.clicked.connect(self.setrect)
        self.showButton.clicked.connect(self.setshow)
        self.magicButton.clicked.connect(self.setmagic)
        self.editButton.clicked.connect(self.setedit)
        self.selectPlus.clicked.connect(self.changedPlus)
        self.selectMinus.clicked.connect(self.changedMinus)
        self.selectPlus.setChecked(True)
        self.selectMinus.setChecked(False)
        self.cancelButton.clicked.connect(self.cancel)
        self.flushButton.clicked.connect(self.flush)
        self.cancelAllButton.clicked.connect(self.box.cancellAll)
        self.finishButton.clicked.connect(self.box.svgfinish)
        self.tsvButton.clicked.connect(self.box.listFinish)
        a = hex(qRgb(0, 0, 0))
        self.colorLabel.setStyleSheet("background-color: #" + a[2:])

    def cancel(self):
        self.box.cancel()

    def flush(self):
        self.box.paintSelect()
        a = hex(qRgb(int(self.lineEdit_R.text()), int(self.lineEdit_G.text()), int(self.lineEdit_B.text())))
        self.colorLabel.setStyleSheet("background-color: #" + a[2:])

    def changedMinus(self):
        self.selectPlus.setChecked(not self.selectPlus.isChecked())
        self.box.selectMinusOrPlus = not self.box.selectMinusOrPlus

    def changedPlus(self):
        self.selectMinus.setChecked(not self.selectMinus.isChecked())
        self.box.selectMinusOrPlus = not self.box.selectMinusOrPlus

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1647, 757)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.formLayout_4 = QtWidgets.QFormLayout(self.centralwidget)
        self.formLayout_4.setObjectName("formLayout_4")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        spacerItem = QtWidgets.QSpacerItem(38, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem1 = QtWidgets.QSpacerItem(78, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.formLayout_2 = QtWidgets.QFormLayout()
        self.formLayout_2.setObjectName("formLayout_2")
        self.openFileButton = QtWidgets.QPushButton(self.centralwidget)
        self.openFileButton.setObjectName("openFileButton")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.openFileButton)
        self.editButton = QtWidgets.QPushButton(self.centralwidget)
        self.editButton.setObjectName("editButton")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.editButton)
        self.showButton = QtWidgets.QCheckBox(self.centralwidget)
        self.showButton.setObjectName("showButton")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.showButton)
        self.rectButton = QtWidgets.QCheckBox(self.centralwidget)
        self.rectButton.setObjectName("rectButton")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.rectButton)
        self.magicButton = QtWidgets.QCheckBox(self.centralwidget)
        self.magicButton.setObjectName("magicButton")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.magicButton)
        self.penButton = QtWidgets.QCheckBox(self.centralwidget)
        self.penButton.setObjectName("penButton")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.penButton)
        self.horizontalLayout.addLayout(self.formLayout_2)
        spacerItem2 = QtWidgets.QSpacerItem(28, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.verticalLayout.addLayout(self.horizontalLayout)
        spacerItem3 = QtWidgets.QSpacerItem(20, 188, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem3)
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.lineEdit_magic = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_magic.setObjectName("lineEdit_magic")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.lineEdit_magic)
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.lineEdit_pensize = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_pensize.setObjectName("lineEdit_pensize")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.lineEdit_pensize)
        self.verticalLayout.addLayout(self.formLayout)
        spacerItem4 = QtWidgets.QSpacerItem(20, 168, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem4)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 0, 0, 1, 1)
        self.selectMinus = QtWidgets.QCheckBox(self.centralwidget)
        self.selectMinus.setObjectName("selectMinus")
        self.gridLayout.addWidget(self.selectMinus, 3, 1, 1, 1)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.gridLayout.addLayout(self.verticalLayout_3, 5, 1, 1, 1)
        self.colorLabel = QtWidgets.QLabel(self.centralwidget)
        self.colorLabel.setObjectName("colorLabel")
        self.gridLayout.addWidget(self.colorLabel, 0, 1, 1, 1)
        self.selectPlus = QtWidgets.QCheckBox(self.centralwidget)
        self.selectPlus.setObjectName("selectPlus")
        self.gridLayout.addWidget(self.selectPlus, 2, 1, 1, 1)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_3.addWidget(self.label_4)
        self.lineEdit_R = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_R.setObjectName("lineEdit_R")
        self.horizontalLayout_3.addWidget(self.lineEdit_R)
        self.gridLayout.addLayout(self.horizontalLayout_3, 2, 0, 1, 1)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_4.addWidget(self.label_5)
        self.lineEdit_G = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_G.setObjectName("lineEdit_G")
        self.horizontalLayout_4.addWidget(self.lineEdit_G)
        self.gridLayout.addLayout(self.horizontalLayout_4, 3, 0, 1, 1)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_5.addWidget(self.label_6)
        self.lineEdit_B = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_B.setObjectName("lineEdit_B")
        self.horizontalLayout_5.addWidget(self.lineEdit_B)
        self.gridLayout.addLayout(self.horizontalLayout_5, 5, 0, 1, 1)
        self.flushButton = QtWidgets.QPushButton(self.centralwidget)
        self.flushButton.setObjectName("flushButton")
        self.gridLayout.addWidget(self.flushButton, 6, 0, 1, 1)
        self.cancelButton = QtWidgets.QPushButton(self.centralwidget)
        self.cancelButton.setObjectName("cancelButton")
        self.gridLayout.addWidget(self.cancelButton, 8, 0, 1, 1)
        self.cancelAllButton = QtWidgets.QPushButton(self.centralwidget)
        self.cancelAllButton.setObjectName("cancelAllButton")
        self.gridLayout.addWidget(self.cancelAllButton, 9, 0, 1, 1)
        self.finishButton = QtWidgets.QPushButton(self.centralwidget)
        self.finishButton.setObjectName("finishButton")
        self.gridLayout.addWidget(self.finishButton, 8, 1, 1, 1)
        self.tsvButton = QtWidgets.QPushButton(self.centralwidget)
        self.tsvButton.setObjectName("tsvButton")
        self.gridLayout.addWidget(self.tsvButton, 9, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        self.formLayout_4.setLayout(0, QtWidgets.QFormLayout.LabelRole, self.horizontalLayout_2)

        self.scrollArea = QtWidgets.QScrollArea(self.centralwidget)
        self.scrollArea.setMouseTracking(False)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 1339, 695))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.box = ImageBox(self.lineEdit_B,
                            self.lineEdit_G,
                            self.lineEdit_R,
                            self.lineEdit_pensize,
                            self.lineEdit_magic)
        self.gridLayout = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout.addWidget(self.box, 0, 0, 1, 1)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.formLayout_4.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.scrollArea)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1647, 22))
        self.menubar.setObjectName("menubar")
        self.menu = QtWidgets.QMenu(self.menubar)
        self.menu.setObjectName("menu")
        self.settingMenu = QtWidgets.QMenu(self.menubar)
        self.settingMenu.setObjectName("settingMenu")
        self.menu_2 = QtWidgets.QMenu(self.settingMenu)
        self.menu_2.setObjectName("menu_2")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionpng = QtWidgets.QAction(MainWindow)
        self.actionpng.setObjectName("actionpng")
        self.action_select = QtWidgets.QAction(MainWindow)
        self.action_select.setObjectName("action_select")
        self.action_svg = QtWidgets.QAction(MainWindow)
        self.action_svg.setObjectName("action_svg")
        self.action_out = QtWidgets.QAction(MainWindow)
        self.action_out.setObjectName("action_out")
        self.actionzh = QtWidgets.QAction(MainWindow)
        self.actionzh.setObjectName("actionzh")
        self.actionen = QtWidgets.QAction(MainWindow)
        self.actionen.setObjectName("actionen")
        self.actionFranch = QtWidgets.QAction(MainWindow)
        self.actionFranch.setObjectName("actionFranch")
        self.actionGerman = QtWidgets.QAction(MainWindow)
        self.actionGerman.setObjectName("actionGerman")
        self.actionJapenese = QtWidgets.QAction(MainWindow)
        self.actionJapenese.setObjectName("actionJapenese")
        self.actionalabo = QtWidgets.QAction(MainWindow)
        self.actionalabo.setObjectName("actionalabo")
        self.actionlading = QtWidgets.QAction(MainWindow)
        self.actionlading.setObjectName("actionlading")
        self.actionxibolai = QtWidgets.QAction(MainWindow)
        self.actionxibolai.setObjectName("actionxibolai")
        self.actionselect = QtWidgets.QAction(MainWindow)
        self.actionselect.setObjectName("actionselect")
        self.actioncut = QtWidgets.QAction(MainWindow)
        self.actioncut.setObjectName("actioncut")
        self.menu.addAction(self.actioncut)
        self.menu.addAction(self.actionselect)
        self.menu_2.addAction(self.actionzh)
        self.menu_2.addAction(self.actionen)
        self.menu_2.addAction(self.actionFranch)
        self.menu_2.addAction(self.actionGerman)
        self.menu_2.addAction(self.actionJapenese)
        self.menu_2.addAction(self.actionalabo)
        self.menu_2.addAction(self.actionlading)
        self.menu_2.addAction(self.actionxibolai)
        self.settingMenu.addSeparator()
        self.settingMenu.addAction(self.menu_2.menuAction())
        self.menubar.addAction(self.menu.menuAction())
        self.menubar.addAction(self.settingMenu.menuAction())
        self.actionen.triggered.connect(self.changeToEnglish)
        self.actionalabo.triggered.connect(self.changeToArabic)
        self.actionzh.triggered.connect(self.changeToChinese)
        self.actionGerman.triggered.connect(self.changeToGerman)
        self.actionxibolai.triggered.connect(self.changeToHebrew)
        self.actionJapenese.triggered.connect(self.changeToJapanese)
        self.actionlading.triggered.connect(self.changeToLatin)
        self.actionFranch.triggered.connect(self.changeToFrench)

        self.setconnected()
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.openFileButton.setText(_translate("MainWindow", "打开"))
        self.editButton.setText(_translate("MainWindow", "编辑"))
        self.showButton.setText(_translate("MainWindow", "显示"))
        self.rectButton.setText(_translate("MainWindow", "多边形套索"))
        self.magicButton.setText(_translate("MainWindow", "魔棒"))
        self.penButton.setText(_translate("MainWindow", "钢笔"))
        self.lineEdit_magic.setText(_translate("MainWindow", "100"))
        self.label.setText(_translate("MainWindow", "魔棒容差："))
        self.label_2.setText(_translate("MainWindow", "笔刷大小："))
        self.lineEdit_pensize.setText(_translate("MainWindow", "10"))
        self.label_3.setText(_translate("MainWindow", "框选比较色"))
        self.selectMinus.setText(_translate("MainWindow", "选中-"))
        self.colorLabel.setText(_translate("MainWindow", "TextLabel"))
        self.selectPlus.setText(_translate("MainWindow", "选中+"))
        self.label_4.setText(_translate("MainWindow", "R"))
        self.lineEdit_R.setText(_translate("MainWindow", "0"))
        self.label_5.setText(_translate("MainWindow", "G"))
        self.lineEdit_G.setText(_translate("MainWindow", "0"))
        self.label_6.setText(_translate("MainWindow", "B"))
        self.lineEdit_B.setText(_translate("MainWindow", "0"))
        self.flushButton.setText(_translate("MainWindow", "确定更新颜色"))
        self.cancelButton.setText(_translate("MainWindow", "撤销重做"))
        self.cancelAllButton.setText(_translate("MainWindow", "全部重做"))
        self.finishButton.setText(_translate("MainWindow", "裁剪SVG"))
        self.tsvButton.setText(_translate("MainWindow", "输出tsv表格"))
        self.menu.setTitle(_translate("MainWindow", "开始"))
        self.settingMenu.setTitle(_translate("MainWindow", "设置"))
        self.menu_2.setTitle(_translate("MainWindow", "语言"))
        self.actionpng.setText(_translate("MainWindow", "png处理"))
        self.action_select.setText(_translate("MainWindow", "选区处理"))
        self.action_svg.setText(_translate("MainWindow", "导入svg"))
        self.action_out.setText(_translate("MainWindow", "输出"))
        self.actionzh.setText(_translate("MainWindow", "中文"))
        self.actionen.setText(_translate("MainWindow", "English"))
        self.actionFranch.setText(_translate("MainWindow", "Français"))
        self.actionGerman.setText(_translate("MainWindow", "Deutsch"))
        self.actionJapenese.setText(_translate("MainWindow", "日本語"))
        self.actionalabo.setText(_translate("MainWindow", "اللغة العربية"))
        self.actionlading.setText(_translate("MainWindow", "Lingua Latīna"))
        self.actionxibolai.setText(_translate("MainWindow", "עִבְרִית"))
        self.actionselect.setText(_translate("MainWindow", "步骤二 选区"))
        self.actioncut.setText(_translate("MainWindow", "步骤一 裁剪"))

    def changeLanguage(self, lan):
        if lan == Language.Chi:
            self.changeToChinese()
        elif lan == Language.Eng:
            self.changeToEnglish()
        elif lan == Language.Fra:
            self.changeToFrench()
        elif lan == Language.Ger:
            self.changeToGerman()
        elif lan == Language.Jan:
            self.changeToJapanese()
        elif lan == Language.Alo:
            self.changeToArabic()
        elif lan == Language.Lad:
            self.changeToLatin()
        elif lan == Language.Hib:
            self.changeToHebrew()

    def changeToChinese(self):
        path = "language/choose/chn_choose.qm"
        path = config.resource_path(path)
        self.translator.load(path)
        QApplication.instance().installTranslator(self.translator)
        self.retranslateUi(QtWidgets.QMainWindow())
        config.now_Lan = Language.Chi

    def changeToEnglish(self):
        path = "language/choose/eng_choose .qm"
        path = config.resource_path(path)
        self.translator.load(path)
        QApplication.instance().installTranslator(self.translator)
        self.retranslateUi(QtWidgets.QMainWindow())
        config.now_Lan = Language.Eng

    def changeToFrench(self):
        path = "language/choose/fra_choose .qm"
        path = config.resource_path(path)
        self.translator.load(path)
        QApplication.instance().installTranslator(self.translator)
        self.retranslateUi(QtWidgets.QMainWindow())
        config.now_Lan = Language.Fra

    def changeToGerman(self):
        path = "language/choose/ger_choose .qm"
        path = config.resource_path(path)
        self.translator.load(path)
        QApplication.instance().installTranslator(self.translator)
        self.retranslateUi(QtWidgets.QMainWindow())
        config.now_Lan = Language.Ger

    def changeToJapanese(self):
        path = "language/choose/jan_choose.qm"
        path = config.resource_path(path)
        self.translator.load(path)
        QApplication.instance().installTranslator(self.translator)
        self.retranslateUi(QtWidgets.QMainWindow())
        config.now_Lan = Language.Jan

    def changeToArabic(self):
        path = "language/choose/alo_choose.qm"
        path = config.resource_path(path)
        self.translator.load(path)
        QApplication.instance().installTranslator(self.translator)
        self.retranslateUi(QtWidgets.QMainWindow())
        config.now_Lan = Language.Alo

    def changeToLatin(self):
        path = "language/choose/lad_choose.qm"
        path = config.resource_path(path)
        self.translator.load(path)
        QApplication.instance().installTranslator(self.translator)
        self.retranslateUi(QtWidgets.QMainWindow())
        config.now_Lan = Language.Lad

    def changeToHebrew(self):
        path = "language/choose/hib_choose.qm"
        path = config.resource_path(path)
        self.translator.load(path)
        QApplication.instance().installTranslator(self.translator)
        self.retranslateUi(QtWidgets.QMainWindow())
        config.now_Lan = Language.Hib

    # def setupUi(self, MainWindow):
    #     MainWindow.setObjectName("MainWindow")
    #     MainWindow.resize(1647, 757)
    #     self.centralwidget = QtWidgets.QWidget(MainWindow)
    #     self.centralwidget.setObjectName("centralwidget")
    #     self.formLayout_4 = QtWidgets.QFormLayout(self.centralwidget)
    #     self.formLayout_4.setObjectName("formLayout_4")
    #     self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
    #     self.horizontalLayout_2.setObjectName("horizontalLayout_2")
    #     self.verticalLayout = QtWidgets.QVBoxLayout()
    #     self.verticalLayout.setObjectName("verticalLayout")
    #     spacerItem = QtWidgets.QSpacerItem(38, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
    #     self.verticalLayout.addItem(spacerItem)
    #     self.horizontalLayout = QtWidgets.QHBoxLayout()
    #     self.horizontalLayout.setObjectName("horizontalLayout")
    #     spacerItem1 = QtWidgets.QSpacerItem(78, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
    #     self.horizontalLayout.addItem(spacerItem1)
    #     self.formLayout_2 = QtWidgets.QFormLayout()
    #     self.formLayout_2.setObjectName("formLayout_2")
    #     self.openFileButton = QtWidgets.QPushButton(self.centralwidget)
    #     self.openFileButton.setObjectName("openFileButton")
    #     self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.openFileButton)
    #     self.editButton = QtWidgets.QPushButton(self.centralwidget)
    #     self.editButton.setObjectName("editButton")
    #     self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.editButton)
    #     self.showButton = QtWidgets.QCheckBox(self.centralwidget)
    #     self.showButton.setObjectName("showButton")
    #     self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.showButton)
    #     self.rectButton = QtWidgets.QCheckBox(self.centralwidget)
    #     self.rectButton.setObjectName("rectButton")
    #     self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.rectButton)
    #     self.magicButton = QtWidgets.QCheckBox(self.centralwidget)
    #     self.magicButton.setObjectName("magicButton")
    #     self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.magicButton)
    #     self.penButton = QtWidgets.QCheckBox(self.centralwidget)
    #     self.penButton.setObjectName("penButton")
    #     self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.penButton)
    #     self.horizontalLayout.addLayout(self.formLayout_2)
    #     spacerItem2 = QtWidgets.QSpacerItem(28, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
    #     self.horizontalLayout.addItem(spacerItem2)
    #     self.verticalLayout.addLayout(self.horizontalLayout)
    #     spacerItem3 = QtWidgets.QSpacerItem(20, 188, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
    #     self.verticalLayout.addItem(spacerItem3)
    #     self.formLayout = QtWidgets.QFormLayout()
    #     self.formLayout.setObjectName("formLayout")
    #     self.lineEdit_magic = QtWidgets.QLineEdit(self.centralwidget)
    #     self.lineEdit_magic.setObjectName("lineEdit_magic")
    #     self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.lineEdit_magic)
    #     self.label = QtWidgets.QLabel(self.centralwidget)
    #     self.label.setObjectName("label")
    #     self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
    #     self.label_2 = QtWidgets.QLabel(self.centralwidget)
    #     self.label_2.setObjectName("label_2")
    #     self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
    #     self.lineEdit_pensize = QtWidgets.QLineEdit(self.centralwidget)
    #     self.lineEdit_pensize.setObjectName("lineEdit_pensize")
    #     self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.lineEdit_pensize)
    #     self.verticalLayout.addLayout(self.formLayout)
    #     spacerItem4 = QtWidgets.QSpacerItem(20, 168, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
    #     self.verticalLayout.addItem(spacerItem4)
    #     self.gridLayout = QtWidgets.QGridLayout()
    #     self.gridLayout.setObjectName("gridLayout")
    #     self.label_3 = QtWidgets.QLabel(self.centralwidget)
    #     self.label_3.setObjectName("label_3")
    #     self.gridLayout.addWidget(self.label_3, 0, 0, 1, 1)
    #     self.selectMinus = QtWidgets.QCheckBox(self.centralwidget)
    #     self.selectMinus.setObjectName("selectMinus")
    #     self.gridLayout.addWidget(self.selectMinus, 3, 1, 1, 1)
    #     self.verticalLayout_3 = QtWidgets.QVBoxLayout()
    #     self.verticalLayout_3.setObjectName("verticalLayout_3")
    #     self.gridLayout.addLayout(self.verticalLayout_3, 5, 1, 1, 1)
    #     self.colorLabel = QtWidgets.QLabel(self.centralwidget)
    #     self.colorLabel.setObjectName("colorLabel")
    #     self.gridLayout.addWidget(self.colorLabel, 0, 1, 1, 1)
    #     self.selectPlus = QtWidgets.QCheckBox(self.centralwidget)
    #     self.selectPlus.setObjectName("selectPlus")
    #     self.gridLayout.addWidget(self.selectPlus, 2, 1, 1, 1)
    #     self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
    #     self.horizontalLayout_3.setObjectName("horizontalLayout_3")
    #     self.label_4 = QtWidgets.QLabel(self.centralwidget)
    #     self.label_4.setObjectName("label_4")
    #     self.horizontalLayout_3.addWidget(self.label_4)
    #     self.lineEdit_R = QtWidgets.QLineEdit(self.centralwidget)
    #     self.lineEdit_R.setObjectName("lineEdit_R")
    #     self.horizontalLayout_3.addWidget(self.lineEdit_R)
    #     self.gridLayout.addLayout(self.horizontalLayout_3, 2, 0, 1, 1)
    #     self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
    #     self.horizontalLayout_4.setObjectName("horizontalLayout_4")
    #     self.label_5 = QtWidgets.QLabel(self.centralwidget)
    #     self.label_5.setObjectName("label_5")
    #     self.horizontalLayout_4.addWidget(self.label_5)
    #     self.lineEdit_G = QtWidgets.QLineEdit(self.centralwidget)
    #     self.lineEdit_G.setObjectName("lineEdit_G")
    #     self.horizontalLayout_4.addWidget(self.lineEdit_G)
    #     self.gridLayout.addLayout(self.horizontalLayout_4, 3, 0, 1, 1)
    #     self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
    #     self.horizontalLayout_5.setObjectName("horizontalLayout_5")
    #     self.label_6 = QtWidgets.QLabel(self.centralwidget)
    #     self.label_6.setObjectName("label_6")
    #     self.horizontalLayout_5.addWidget(self.label_6)
    #     self.lineEdit_B = QtWidgets.QLineEdit(self.centralwidget)
    #     self.lineEdit_B.setObjectName("lineEdit_B")
    #     self.horizontalLayout_5.addWidget(self.lineEdit_B)
    #     self.gridLayout.addLayout(self.horizontalLayout_5, 5, 0, 1, 1)
    #     self.flushButton = QtWidgets.QPushButton(self.centralwidget)
    #     self.flushButton.setObjectName("flushButton")
    #     self.gridLayout.addWidget(self.flushButton, 6, 0, 1, 1)
    #     self.cancelButton = QtWidgets.QPushButton(self.centralwidget)
    #     self.cancelButton.setObjectName("cancelButton")
    #     self.gridLayout.addWidget(self.cancelButton, 8, 0, 1, 1)
    #     self.cancelAllButton = QtWidgets.QPushButton(self.centralwidget)
    #     self.cancelAllButton.setObjectName("cancelAllButton")
    #     self.gridLayout.addWidget(self.cancelAllButton, 9, 0, 1, 1)
    #     self.finishButton = QtWidgets.QPushButton(self.centralwidget)
    #     self.finishButton.setObjectName("finishButton")
    #     self.gridLayout.addWidget(self.finishButton, 8, 1, 1, 1)
    #     self.tsvButton = QtWidgets.QPushButton(self.centralwidget)
    #     self.tsvButton.setObjectName("tsvButton")
    #     self.gridLayout.addWidget(self.tsvButton, 9, 1, 1, 1)
    #     self.verticalLayout.addLayout(self.gridLayout)
    #     self.horizontalLayout_2.addLayout(self.verticalLayout)
    #     self.formLayout_4.setLayout(0, QtWidgets.QFormLayout.LabelRole, self.horizontalLayout_2)
    #
    #     self.scrollArea = QtWidgets.QScrollArea(self.centralwidget)
    #     self.scrollArea.setMouseTracking(False)
    #     self.scrollArea.setWidgetResizable(True)
    #     self.scrollArea.setObjectName("scrollArea")
    #     self.scrollAreaWidgetContents = QtWidgets.QWidget()
    #     self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 1339, 695))
    #     self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
    #     self.scrollArea.setWidget(self.scrollAreaWidgetContents)
    #
    #     self.box = ImageBox(self.lineEdit_B,
    #                         self.lineEdit_G,
    #                         self.lineEdit_R,
    #                         self.lineEdit_pensize,
    #                         self.lineEdit_magic)
    #     self.gridLayout = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)
    #     self.gridLayout.setObjectName("gridLayout")
    #     self.gridLayout.addWidget(self.box, 0, 0, 1, 1)
    #     self.scrollArea.setWidget(self.scrollAreaWidgetContents)
    #
    #     self.formLayout_4.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.scrollArea)
    #
    #     MainWindow.setCentralWidget(self.centralwidget)
    #     self.menubar = QtWidgets.QMenuBar(MainWindow)
    #     self.menubar.setGeometry(QtCore.QRect(0, 0, 1647, 22))
    #     self.menubar.setObjectName("menubar")
    #     self.menu = QtWidgets.QMenu(self.menubar)
    #     self.menu.setObjectName("menu")
    #     MainWindow.setMenuBar(self.menubar)
    #     self.statusbar = QtWidgets.QStatusBar(MainWindow)
    #     self.statusbar.setObjectName("statusbar")
    #     MainWindow.setStatusBar(self.statusbar)
    #     self.actionpng = QtWidgets.QAction(MainWindow)
    #     self.actionpng.setObjectName("actionpng")
    #     self.action_select = QtWidgets.QAction(MainWindow)
    #     self.action_select.setObjectName("action_select")
    #     self.action_svg = QtWidgets.QAction(MainWindow)
    #     self.action_svg.setObjectName("action_svg")
    #     self.action_out = QtWidgets.QAction(MainWindow)
    #     self.action_out.setObjectName("action_out")
    #     self.menu.addAction(self.actionpng)
    #     self.menu.addAction(self.action_select)
    #     self.menu.addAction(self.action_svg)
    #     self.menu.addAction(self.action_out)
    #     self.menubar.addAction(self.menu.menuAction())
    #
    #     self.setconnected()
    #     self.retranslateUi(MainWindow)
    #     QtCore.QMetaObject.connectSlotsByName(MainWindow)
    #
    # def retranslateUi(self, MainWindow):
    #     _translate = QtCore.QCoreApplication.translate
    #     MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
    #     self.openFileButton.setText(_translate("MainWindow", "打开"))
    #     self.editButton.setText(_translate("MainWindow", "编辑"))
    #     self.showButton.setText(_translate("MainWindow", "显示"))
    #     self.rectButton.setText(_translate("MainWindow", "多边形套索"))
    #     self.magicButton.setText(_translate("MainWindow", "魔棒"))
    #     self.penButton.setText(_translate("MainWindow", "钢笔"))
    #     self.lineEdit_magic.setText(_translate("MainWindow", "100"))
    #     self.label.setText(_translate("MainWindow", "魔棒容差："))
    #     self.label_2.setText(_translate("MainWindow", "笔刷大小："))
    #     self.lineEdit_pensize.setText(_translate("MainWindow", "10"))
    #     self.label_3.setText(_translate("MainWindow", "框选比较色"))
    #     self.selectMinus.setText(_translate("MainWindow", "选中-"))
    #     self.colorLabel.setText(_translate("MainWindow", "TextLabel"))
    #     self.selectPlus.setText(_translate("MainWindow", "选中+"))
    #
    #     self.label_4.setText(_translate("MainWindow", "R"))
    #     self.lineEdit_R.setText(_translate("MainWindow", "0"))
    #     self.label_5.setText(_translate("MainWindow", "G"))
    #     self.lineEdit_G.setText(_translate("MainWindow", "0"))
    #     self.label_6.setText(_translate("MainWindow", "B"))
    #     self.lineEdit_B.setText(_translate("MainWindow", "0"))
    #     self.flushButton.setText(_translate("MainWindow", "确定更新颜色"))
    #     self.cancelButton.setText(_translate("MainWindow", "撤销重做"))
    #     self.cancelAllButton.setText(_translate("MainWindow", "全部重做"))
    #     self.finishButton.setText(_translate("MainWindow", "裁剪SVG"))
    #     self.tsvButton.setText(_translate("MainWindow", "输出tsv表格"))
    #     self.menu.setTitle(_translate("MainWindow", "开始"))
    #     self.actionpng.setText(_translate("MainWindow", "png处理"))
    #     self.action_select.setText(_translate("MainWindow", "选区处理"))
    #     self.action_svg.setText(_translate("MainWindow", "导入svg"))
    #     self.action_out.setText(_translate("MainWindow", "输出"))

    def setpen(self):
        self.box.rectOp = True
        self.box.PolygonOp = False
        self.box.MagicOp = False
        self.magicButton.setChecked(False)
        self.penButton.setChecked(True)
        self.rectButton.setChecked(False)
        self.box.polyList = []

    def setrect(self):
        self.box.rectOp = False
        self.box.PolygonOp = True
        self.box.MagicOp = False
        self.magicButton.setChecked(False)
        self.penButton.setChecked(False)
        self.rectButton.setChecked(True)
        self.box.polyList = []

    def setmagic(self):
        self.box.rectOp = False
        self.box.PolygonOp = False
        self.box.MagicOp = True
        self.magicButton.setChecked(True)
        self.penButton.setChecked(False)
        self.rectButton.setChecked(False)
        self.box.polyList = []

    def setedit(self):
        if self.box.edit == True:
            self.box.edit = False
        else:
            self.box.edit = True

    def setshow(self):
        if self.box.showSelect == True:
            self.box.showSelect = False
        else:
            self.box.showSelect = True
        self.box.repaint()

    def open_image(self):
        """
        select image file and open it
        :return:
        """
        # img_name, _ = QFileDialog.getOpenFileName(self, "打开图片", "", "All Files(*);;*.jpg;;*.png")
        img_name, _ = QFileDialog.getOpenFileName(None, "Open Image File", "", "")
        if img_name != "":
            img = QPixmap(img_name)
            print(img.width(), "+", img.height())

            self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, img.width(), img.height()))
            self.box.set_image(img_name)
            self.arraylist = numpy.zeros((img.width(), img.height()))

    def edit(self):
        self.widthpng = self.image.width()
        self.heightpng = self.image.height()
        num = [[0 for i in range(0, self.image.width())] for j in range(0, self.image.height())]
        for i in range(0, self.widthpng):
            for j in range(0, self.widthpng):
                num[i][j] = False

        p = QPixmap(self.width(), self.height())
        p.fill(QColor(0, 0, 0, 127))
        self.labelCom.setPixmap(p)
        self.labelCom.setGeometry(0, self.myButton.height(), self.width(), self.height())
        self.label.setVisible(False)
        self.labelCom.setVisible(True)


def source_path(relative_path):
    # 是否Bundle Resource
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# 修改当前工作目录，使得资源文件可以被正确访问
if __name__ == "__main__":
    cd = source_path('')
    os.chdir(cd)
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = UI()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
