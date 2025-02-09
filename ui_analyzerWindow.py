# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'analyzerWindow.ui'
##
## Created by: Qt User Interface Compiler version 6.8.1
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
from PySide6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QHeaderView,
    QLabel, QMainWindow, QPushButton, QSizePolicy,
    QSlider, QStatusBar, QTreeWidget, QTreeWidgetItem,
    QVBoxLayout, QWidget)

from pyqtgraph import GraphicsLayoutWidget

class Ui_analyzerWindow(object):
    def setupUi(self, analyzerWindow):
        if not analyzerWindow.objectName():
            analyzerWindow.setObjectName(u"analyzerWindow")
        analyzerWindow.resize(1007, 768)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(analyzerWindow.sizePolicy().hasHeightForWidth())
        analyzerWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QWidget(analyzerWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_2 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.container_filepicker = QHBoxLayout()
        self.container_filepicker.setObjectName(u"container_filepicker")
        self.label_filepicker = QLabel(self.centralwidget)
        self.label_filepicker.setObjectName(u"label_filepicker")
        self.label_filepicker.setMaximumSize(QSize(80, 16777215))
        self.label_filepicker.setTextFormat(Qt.TextFormat.PlainText)
        self.label_filepicker.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

        self.container_filepicker.addWidget(self.label_filepicker)

        self.combo_filepicker = QComboBox(self.centralwidget)
        self.combo_filepicker.setObjectName(u"combo_filepicker")

        self.container_filepicker.addWidget(self.combo_filepicker)


        self.verticalLayout_2.addLayout(self.container_filepicker)

        self.container_graphics_control = QWidget(self.centralwidget)
        self.container_graphics_control.setObjectName(u"container_graphics_control")
        self.container_graphics_control.setEnabled(False)
        self.horizontalLayout_4 = QHBoxLayout(self.container_graphics_control)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.graphics_layout = GraphicsLayoutWidget(self.container_graphics_control)
        self.graphics_layout.setObjectName(u"graphics_layout")
        palette = QPalette()
        brush = QBrush(QColor(255, 255, 255, 255))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.WindowText, brush)
        brush1 = QBrush(QColor(0, 0, 0, 255))
        brush1.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Button, brush1)
        palette.setBrush(QPalette.Active, QPalette.Light, brush1)
        palette.setBrush(QPalette.Active, QPalette.Midlight, brush1)
        palette.setBrush(QPalette.Active, QPalette.Dark, brush1)
        palette.setBrush(QPalette.Active, QPalette.Mid, brush1)
        palette.setBrush(QPalette.Active, QPalette.Text, brush)
        palette.setBrush(QPalette.Active, QPalette.BrightText, brush)
        palette.setBrush(QPalette.Active, QPalette.ButtonText, brush)
        palette.setBrush(QPalette.Active, QPalette.Base, brush1)
        palette.setBrush(QPalette.Active, QPalette.Window, brush1)
        palette.setBrush(QPalette.Active, QPalette.Shadow, brush1)
        palette.setBrush(QPalette.Active, QPalette.AlternateBase, brush1)
        brush2 = QBrush(QColor(255, 255, 220, 255))
        brush2.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.ToolTipBase, brush2)
        palette.setBrush(QPalette.Active, QPalette.ToolTipText, brush1)
        brush3 = QBrush(QColor(255, 255, 255, 127))
        brush3.setStyle(Qt.SolidPattern)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.Active, QPalette.PlaceholderText, brush3)
#endif
        palette.setBrush(QPalette.Active, QPalette.Accent, brush1)
        palette.setBrush(QPalette.Inactive, QPalette.WindowText, brush)
        palette.setBrush(QPalette.Inactive, QPalette.Button, brush1)
        palette.setBrush(QPalette.Inactive, QPalette.Light, brush1)
        palette.setBrush(QPalette.Inactive, QPalette.Midlight, brush1)
        palette.setBrush(QPalette.Inactive, QPalette.Dark, brush1)
        palette.setBrush(QPalette.Inactive, QPalette.Mid, brush1)
        palette.setBrush(QPalette.Inactive, QPalette.Text, brush)
        palette.setBrush(QPalette.Inactive, QPalette.BrightText, brush)
        palette.setBrush(QPalette.Inactive, QPalette.ButtonText, brush)
        palette.setBrush(QPalette.Inactive, QPalette.Base, brush1)
        palette.setBrush(QPalette.Inactive, QPalette.Window, brush1)
        palette.setBrush(QPalette.Inactive, QPalette.Shadow, brush1)
        palette.setBrush(QPalette.Inactive, QPalette.AlternateBase, brush1)
        palette.setBrush(QPalette.Inactive, QPalette.ToolTipBase, brush2)
        palette.setBrush(QPalette.Inactive, QPalette.ToolTipText, brush1)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.Inactive, QPalette.PlaceholderText, brush3)
#endif
        palette.setBrush(QPalette.Inactive, QPalette.Accent, brush1)
        palette.setBrush(QPalette.Disabled, QPalette.WindowText, brush1)
        palette.setBrush(QPalette.Disabled, QPalette.Button, brush1)
        palette.setBrush(QPalette.Disabled, QPalette.Light, brush1)
        palette.setBrush(QPalette.Disabled, QPalette.Midlight, brush1)
        palette.setBrush(QPalette.Disabled, QPalette.Dark, brush1)
        palette.setBrush(QPalette.Disabled, QPalette.Mid, brush1)
        palette.setBrush(QPalette.Disabled, QPalette.Text, brush1)
        palette.setBrush(QPalette.Disabled, QPalette.BrightText, brush)
        palette.setBrush(QPalette.Disabled, QPalette.ButtonText, brush1)
        palette.setBrush(QPalette.Disabled, QPalette.Base, brush1)
        palette.setBrush(QPalette.Disabled, QPalette.Window, brush1)
        palette.setBrush(QPalette.Disabled, QPalette.Shadow, brush1)
        palette.setBrush(QPalette.Disabled, QPalette.AlternateBase, brush1)
        palette.setBrush(QPalette.Disabled, QPalette.ToolTipBase, brush2)
        palette.setBrush(QPalette.Disabled, QPalette.ToolTipText, brush1)
        brush4 = QBrush(QColor(0, 0, 0, 127))
        brush4.setStyle(Qt.SolidPattern)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.Disabled, QPalette.PlaceholderText, brush4)
#endif
        palette.setBrush(QPalette.Disabled, QPalette.Accent, brush1)
        self.graphics_layout.setPalette(palette)
        self.graphics_layout.setAutoFillBackground(True)

        self.horizontalLayout_4.addWidget(self.graphics_layout)

        self.container_controls = QWidget(self.container_graphics_control)
        self.container_controls.setObjectName(u"container_controls")
        self.container_controls.setMaximumSize(QSize(300, 16777215))
        self.verticalLayout = QVBoxLayout(self.container_controls)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tree_json = QTreeWidget(self.container_controls)
        __qtreewidgetitem = QTreeWidgetItem()
        __qtreewidgetitem.setText(1, u"2");
        __qtreewidgetitem.setText(0, u"1");
        self.tree_json.setHeaderItem(__qtreewidgetitem)
        self.tree_json.setObjectName(u"tree_json")
        self.tree_json.setMaximumSize(QSize(300, 16777215))
        self.tree_json.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.tree_json.setColumnCount(2)
        self.tree_json.header().setVisible(False)

        self.verticalLayout.addWidget(self.tree_json)

        self.label_fft_index = QLabel(self.container_controls)
        self.label_fft_index.setObjectName(u"label_fft_index")
        self.label_fft_index.setTextFormat(Qt.TextFormat.PlainText)
        self.label_fft_index.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

        self.verticalLayout.addWidget(self.label_fft_index)

        self.container_fft_index = QWidget(self.container_controls)
        self.container_fft_index.setObjectName(u"container_fft_index")
        self.container_fft_index.setMaximumSize(QSize(300, 16777215))
        self.horizontalLayout_2 = QHBoxLayout(self.container_fft_index)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.slider_fft_index = QSlider(self.container_fft_index)
        self.slider_fft_index.setObjectName(u"slider_fft_index")
        self.slider_fft_index.setMaximumSize(QSize(260, 16777215))
        self.slider_fft_index.setOrientation(Qt.Orientation.Horizontal)

        self.horizontalLayout_2.addWidget(self.slider_fft_index)

        self.label_fft_index_value = QLabel(self.container_fft_index)
        self.label_fft_index_value.setObjectName(u"label_fft_index_value")
        self.label_fft_index_value.setMaximumSize(QSize(20, 200))
        self.label_fft_index_value.setTextFormat(Qt.TextFormat.PlainText)
        self.label_fft_index_value.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

        self.horizontalLayout_2.addWidget(self.label_fft_index_value)


        self.verticalLayout.addWidget(self.container_fft_index)

        self.label_colormap = QLabel(self.container_controls)
        self.label_colormap.setObjectName(u"label_colormap")
        self.label_colormap.setTextFormat(Qt.TextFormat.PlainText)
        self.label_colormap.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

        self.verticalLayout.addWidget(self.label_colormap)

        self.combo_colormap = QComboBox(self.container_controls)
        self.combo_colormap.setObjectName(u"combo_colormap")
        self.combo_colormap.setMaximumSize(QSize(300, 16777215))

        self.verticalLayout.addWidget(self.combo_colormap)

        self.button_snapshot = QPushButton(self.container_controls)
        self.button_snapshot.setObjectName(u"button_snapshot")
        self.button_snapshot.setMinimumSize(QSize(0, 100))
        self.button_snapshot.setMaximumSize(QSize(300, 16777215))

        self.verticalLayout.addWidget(self.button_snapshot)


        self.horizontalLayout_4.addWidget(self.container_controls)


        self.verticalLayout_2.addWidget(self.container_graphics_control)

        analyzerWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(analyzerWindow)
        self.statusbar.setObjectName(u"statusbar")
        analyzerWindow.setStatusBar(self.statusbar)

        self.retranslateUi(analyzerWindow)

        QMetaObject.connectSlotsByName(analyzerWindow)
    # setupUi

    def retranslateUi(self, analyzerWindow):
        analyzerWindow.setWindowTitle(QCoreApplication.translate("analyzerWindow", u"Prohl\u00ed\u017ee\u010dka dat", None))
        self.label_filepicker.setText(QCoreApplication.translate("analyzerWindow", u"M\u011b\u0159en\u00ed:", None))
        self.label_fft_index.setText(QCoreApplication.translate("analyzerWindow", u"Index FFT", None))
        self.label_fft_index_value.setText(QCoreApplication.translate("analyzerWindow", u"5", None))
        self.label_colormap.setText(QCoreApplication.translate("analyzerWindow", u"Color map", None))
        self.button_snapshot.setText(QCoreApplication.translate("analyzerWindow", u"Snapshot!", None))
    # retranslateUi

