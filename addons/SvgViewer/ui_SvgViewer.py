# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'SvgViewer.ui'
##
## Created by: Qt User Interface Compiler version 6.3.0
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
from PySide6.QtWidgets import (QApplication, QComboBox, QDialog, QHBoxLayout,
    QListView, QPushButton, QSizePolicy, QVBoxLayout,
    QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(508, 426)
        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.button_horizontal_layout = QHBoxLayout()
        self.button_horizontal_layout.setObjectName(u"button_horizontal_layout")
        self.button_horizontal_layout.setContentsMargins(-1, 0, -1, -1)
        self.tree_file_comboBox = QComboBox(Dialog)
        self.tree_file_comboBox.setObjectName(u"tree_file_comboBox")

        self.button_horizontal_layout.addWidget(self.tree_file_comboBox)

        self.tree_file_browse_button = QPushButton(Dialog)
        self.tree_file_browse_button.setObjectName(u"tree_file_browse_button")

        self.button_horizontal_layout.addWidget(self.tree_file_browse_button)

        self.button_horizontal_layout.setStretch(0, 2)

        self.verticalLayout_2.addLayout(self.button_horizontal_layout)

        self.listView = QListView(Dialog)
        self.listView.setObjectName(u"listView")

        self.verticalLayout_2.addWidget(self.listView)


        self.horizontalLayout.addLayout(self.verticalLayout_2)

        self.svg_vertical_layout = QVBoxLayout()
        self.svg_vertical_layout.setObjectName(u"svg_vertical_layout")

        self.horizontalLayout.addLayout(self.svg_vertical_layout)

        self.horizontalLayout.setStretch(1, 6)

        self.verticalLayout.addLayout(self.horizontalLayout)


        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.tree_file_browse_button.setText(QCoreApplication.translate("Dialog", u"Browse", None))
    # retranslateUi

