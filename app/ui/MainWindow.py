# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'MainWindow.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QGridLayout, QHBoxLayout,
    QLabel, QLineEdit, QMainWindow, QMenuBar,
    QPushButton, QSizePolicy, QSpacerItem, QStatusBar,
    QTabWidget, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(545, 449)
        MainWindow.setAcceptDrops(True)
        MainWindow.setAnimated(True)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_2, 2, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.label)

        self.comboBox_UsageMode = QComboBox(self.centralwidget)
        self.comboBox_UsageMode.setObjectName(u"comboBox_UsageMode")

        self.horizontalLayout.addWidget(self.comboBox_UsageMode)

        self.pushButton_SendUsageMode = QPushButton(self.centralwidget)
        self.pushButton_SendUsageMode.setObjectName(u"pushButton_SendUsageMode")

        self.horizontalLayout.addWidget(self.pushButton_SendUsageMode)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_3)

        self.horizontalLayout.setStretch(1, 2)
        self.horizontalLayout.setStretch(3, 3)

        self.gridLayout.addLayout(self.horizontalLayout, 3, 0, 1, 1)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.comboBox_ifaces = QComboBox(self.centralwidget)
        self.comboBox_ifaces.setObjectName(u"comboBox_ifaces")

        self.horizontalLayout_2.addWidget(self.comboBox_ifaces)

        self.pushButton_IfacesRefresh = QPushButton(self.centralwidget)
        self.pushButton_IfacesRefresh.setObjectName(u"pushButton_IfacesRefresh")

        self.horizontalLayout_2.addWidget(self.pushButton_IfacesRefresh)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)


        self.gridLayout.addLayout(self.horizontalLayout_2, 1, 0, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout)

        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setTabPosition(QTabWidget.TabPosition.South)
        self.ZCUL = QWidget()
        self.ZCUL.setObjectName(u"ZCUL")
        self.verticalLayout_3 = QVBoxLayout(self.ZCUL)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_2 = QLabel(self.ZCUL)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_3.addWidget(self.label_2)

        self.lineEdit_MLFuseid = QLineEdit(self.ZCUL)
        self.lineEdit_MLFuseid.setObjectName(u"lineEdit_MLFuseid")

        self.horizontalLayout_3.addWidget(self.lineEdit_MLFuseid)

        self.pushButton_MLFuseIDOn = QPushButton(self.ZCUL)
        self.pushButton_MLFuseIDOn.setObjectName(u"pushButton_MLFuseIDOn")

        self.horizontalLayout_3.addWidget(self.pushButton_MLFuseIDOn)

        self.pushButton_MLFuseIDOff = QPushButton(self.ZCUL)
        self.pushButton_MLFuseIDOff.setObjectName(u"pushButton_MLFuseIDOff")

        self.horizontalLayout_3.addWidget(self.pushButton_MLFuseIDOff)


        self.verticalLayout_3.addLayout(self.horizontalLayout_3)

        self.verticalSpacer = QSpacerItem(20, 178, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer)

        self.tabWidget.addTab(self.ZCUL, "")
        self.ZCUR = QWidget()
        self.ZCUR.setObjectName(u"ZCUR")
        self.verticalLayout_2 = QVBoxLayout(self.ZCUR)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_3 = QLabel(self.ZCUR)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_4.addWidget(self.label_3)

        self.lineEdit_MRFuseID = QLineEdit(self.ZCUR)
        self.lineEdit_MRFuseID.setObjectName(u"lineEdit_MRFuseID")

        self.horizontalLayout_4.addWidget(self.lineEdit_MRFuseID)

        self.pushButton_MRFuseIDOn = QPushButton(self.ZCUR)
        self.pushButton_MRFuseIDOn.setObjectName(u"pushButton_MRFuseIDOn")

        self.horizontalLayout_4.addWidget(self.pushButton_MRFuseIDOn)

        self.pushButton_MRFuseIDOff = QPushButton(self.ZCUR)
        self.pushButton_MRFuseIDOff.setObjectName(u"pushButton_MRFuseIDOff")

        self.horizontalLayout_4.addWidget(self.pushButton_MRFuseIDOff)


        self.verticalLayout_2.addLayout(self.horizontalLayout_4)

        self.verticalSpacer_2 = QSpacerItem(20, 178, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_2)

        self.tabWidget.addTab(self.ZCUR, "")

        self.verticalLayout.addWidget(self.tabWidget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 545, 33))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"UsageMode\u7ec4\u64ad", None))
        self.pushButton_SendUsageMode.setText(QCoreApplication.translate("MainWindow", u"Send", None))
        self.pushButton_IfacesRefresh.setText(QCoreApplication.translate("MainWindow", u"Refresh", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"\u914d\u7535(Hex)", None))
        self.lineEdit_MLFuseid.setPlaceholderText(QCoreApplication.translate("MainWindow", u"0x101", None))
        self.pushButton_MLFuseIDOn.setText(QCoreApplication.translate("MainWindow", u"\u4e0a\u7535", None))
        self.pushButton_MLFuseIDOff.setText(QCoreApplication.translate("MainWindow", u"\u4e0b\u7535", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.ZCUL), QCoreApplication.translate("MainWindow", u"ZCUL", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"\u914d\u7535(Hex)", None))
        self.lineEdit_MRFuseID.setPlaceholderText(QCoreApplication.translate("MainWindow", u"0x101", None))
        self.pushButton_MRFuseIDOn.setText(QCoreApplication.translate("MainWindow", u"\u4e0a\u7535", None))
        self.pushButton_MRFuseIDOff.setText(QCoreApplication.translate("MainWindow", u"\u4e0b\u7535", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.ZCUR), QCoreApplication.translate("MainWindow", u"ZCUR", None))
    # retranslateUi

