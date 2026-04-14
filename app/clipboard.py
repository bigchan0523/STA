from PyQt5 import QtWidgets, QtGui
from io import BytesIO

def copy_text(text: str):
    QtWidgets.QApplication.clipboard().setText(text or "", mode=QtGui.QClipboard.Clipboard)

def copy_img(pil_img):
    buf = BytesIO()
    pil_img.save(buf, format="PNG")
    qimg = QtGui.QImage.fromData(buf.getvalue(), "PNG")
    if not qimg.isNull():
        QtWidgets.QApplication.clipboard().setImage(qimg)
