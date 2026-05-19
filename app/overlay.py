from typing import Optional, List
import webbrowser
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
import ctypes
from ctypes import wintypes

SetWindowPos = ctypes.windll.user32.SetWindowPos
HWND_TOPMOST   = -1
SWP_NOMOVE     = 0x0002
SWP_NOSIZE     = 0x0001
SWP_SHOWWINDOW = 0x0040

def open_dict(text: str):
    url = f"https://dict.naver.com/search.nhn?query={text}"
    webbrowser.open(url)

def open_img_search(text: str):
    url = f"https://www.google.com/search?q={text}&tbm=isch"
    webbrowser.open(url)

class OverlayWindow(QtWidgets.QWidget):
    PADDING = QtCore.QMargins(14, 12, 14, 12)
    
    def __init__(self, rect_global: QtCore.QRect, text: str = "",
                 parent: Optional[QtWidgets.QWidget] = None,
                 font_family: Optional[str] = None,
                 font_size: int = 14):
        super().__init__(parent=None)
        self.original_text = ""
        self.multi_labels = [] # 참조 유지용
        self.is_multi_mode = False

        self.setWindowFlags(
            Qt.Popup
            | Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAutoFillBackground(False)
        self.setFocusPolicy(Qt.StrongFocus)

        # 기준 사각형
        self.base_rect = QtCore.QRect(rect_global)

        self._font = QtGui.QFont(font_family)
        self._font.setPointSize(max(int(font_size), 10))
        self._font.setWeight(QtGui.QFont.Black)
        self._font.setStyleStrategy(QtGui.QFont.PreferAntialias)
        self._font.setLetterSpacing(QtGui.QFont.AbsoluteSpacing, 0.4)

        content = QtWidgets.QWidget()
        content.setAutoFillBackground(False)
        content.setAttribute(Qt.WA_TranslucentBackground, True)

        self._lay = QtWidgets.QVBoxLayout(content)
        self._lay.setContentsMargins(self.PADDING.left(), self.PADDING.top(),
                                     self.PADDING.right(), self.PADDING.bottom())
        self._lay.setSpacing(0)

        # 내용 라벨
        self.label = QtWidgets.QLabel(text, self)
        self.label.setWordWrap(True)
        self.label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.label.setFont(self._font)
        self.label.setStyleSheet("QLabel { background: transparent; color: #FFFFFF; }")

        # 그림자
        shadow = QtWidgets.QGraphicsDropShadowEffect(self.label)
        shadow.setBlurRadius(2.5)
        shadow.setOffset(0, 0)
        shadow.setColor(QtGui.QColor(0, 0, 0, 230))
        self.label.setGraphicsEffect(shadow)

        # 버튼 레이아웃 (검색)
        self.btn_lay = QtWidgets.QHBoxLayout()
        self.btn_lay.setContentsMargins(0, 5, 0, 0)
        self.btn_lay.addStretch(1)
        
        self.btn_dict = QtWidgets.QPushButton("DIC")
        self.btn_dict.setFixedSize(40, 20)
        self.btn_dict.setStyleSheet("background: #444; color: white; font-size: 10px; border-radius: 3px;")
        self.btn_dict.clicked.connect(lambda: open_dict(self.original_text))
        
        self.btn_img = QtWidgets.QPushButton("IMG")
        self.btn_img.setFixedSize(40, 20)
        self.btn_img.setStyleSheet("background: #444; color: white; font-size: 10px; border-radius: 3px;")
        self.btn_img.clicked.connect(lambda: open_img_search(self.original_text))
        
        self.btn_lay.addWidget(self.btn_dict)
        self.btn_lay.addWidget(self.btn_img)

        self._lay.addWidget(self.label)
        self._lay.addLayout(self.btn_lay)

        # 루트 레이아웃
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(content)

        # 초기 배치
        self._relayout()
        self.show()
        self.raise_()
        self.activateWindow()
        self.setFocus(Qt.ActiveWindowFocusReason)

        try:
            hwnd = int(self.winId())
            SetWindowPos(wintypes.HWND(hwnd), HWND_TOPMOST, 0, 0, 0, 0,
                         SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW)
        except Exception:
            pass

    # ---------------- 동적 레이아웃 ----------------
    def _screen_for_rect(self, rect: QtCore.QRect) -> QtGui.QScreen:
        scr = QtWidgets.QApplication.screenAt(rect.center())
        return scr or QtWidgets.QApplication.primaryScreen()

    def _calc_text_height(self, content_width: int) -> int:
        """패딩 제외한 콘텐츠 폭에 맞춰 문단 높이(px)를 계산."""
        doc = QtGui.QTextDocument()
        doc.setDefaultFont(self._font)
        doc.setPlainText(self.label.text())
        doc.setTextWidth(max(1, content_width))
        size = doc.size()  # QSizeF
        return int(size.height() + 0.999)

    def _relayout(self):
        total_w = max(50, self.base_rect.width())
        content_w = total_w - self.PADDING.left() - self.PADDING.right()

        self.label.setFixedWidth(max(1, content_w))
        
        if self.is_multi_mode:
            # 멀티 라벨 중 가장 아래쪽(Bottom) 좌표를 찾아서 전체 높이를 지정합니다.
            # 줄바꿈으로 인해 라벨 높이가 늘어나면 오버레이 창도 함께 길어집니다.
            max_bottom = self.base_rect.height()
            for lbl in self.multi_labels:
                max_bottom = max(max_bottom, lbl.y() + lbl.height())
            
            total_h_needed = max_bottom + 50 
        else:
            text_h = self._calc_text_height(content_w)
            total_h_needed = text_h + self.PADDING.top() + self.PADDING.bottom() + 30 # 버튼 공간 포함

        scr = self._screen_for_rect(self.base_rect)
        sgeo = scr.geometry()

        x = self.base_rect.x()
        y = self.base_rect.y()
        h = total_h_needed

        max_h = sgeo.height()
        if h > max_h:
            h = max_h

        overflow_bottom = (y + h) - (sgeo.y() + sgeo.height())
        if overflow_bottom > 0:
            y = max(sgeo.y(), y - overflow_bottom)

        if x < sgeo.x():
            x = sgeo.x()
        if x + total_w > sgeo.x() + sgeo.width():
            x = (sgeo.x() + sgeo.width()) - total_w

        self.setGeometry(QtCore.QRect(x, y, total_w, h))

    # --------------- API ---------------
    def set_text(self, text: str):
        self.label.setText(text or "")
        self._relayout()

    def set_multi_text(self, final_data: List[dict]):
        """텍스트 줄별 위치에 맞게 멀티 라벨 생성"""
        self.is_multi_mode = True
        
        # 기존 라벨들 제거
        for lbl in self.multi_labels:
            lbl.hide()
            lbl.deleteLater()
        self.multi_labels.clear()
        
        self.label.hide() # 멀티 모드에서는 기본 라벨 숨김
        self.original_text = " ".join(d["text"] for d in final_data)
        
        # 가독성을 위해 텍스트 양이 많으면 폰트 크기를 약간 줄임 (동적 폰트 스케일링)
        total_len = len(self.original_text)
        current_font = QtGui.QFont(self._font)
        if total_len > 400:
            current_font.setPointSize(max(10, current_font.pointSize() - 2))
        if total_len > 800:
            current_font.setPointSize(max(9, current_font.pointSize() - 3))

        # Y 좌표 기준으로 정렬 (위에서 아래로 배치해야 순서가 꼬이지 않음)
        sorted_data = sorted(final_data, key=lambda x: x["rect"][1])
        placed_rects = []

        for item in sorted_data:
            if not item["text"].strip(): continue
            lbl = QtWidgets.QLabel(item["text"], self)
            lbl.setWordWrap(True)
            lbl.setFont(current_font)
            lbl.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            # 글자 배경 및 스타일 (가독성 최우선)
            lbl.setStyleSheet("color: white; background: rgba(0,0,0,180); border: 1px solid rgba(255,255,255,60); border-radius: 4px; padding: 4px;")
            
            # 로컬 좌표 계산
            rx, ry, rw, rh = item["rect"]
            
            # 폭을 원본보다 약간 넓게 설정하여 여유 공간 확보 (최대 1.3배)
            w_fixed = max(int(rw * 1.3) + 20, 80)
            
            # QTextDocument를 활용하여 정확한 텍스트 높이 계산
            doc = QtGui.QTextDocument()
            doc.setDefaultFont(current_font)
            doc.setPlainText(item["text"])
            doc.setTextWidth(w_fixed - 8) # 양쪽 padding(4px * 2) 제외
            needed_h = int(doc.size().height() + 0.999) + 8 # 상하 padding 포함
            
            # 텍스트가 원본 영역보다 길어질 경우를 대비해 충분한 높이 보장
            final_h = max(needed_h + 10, int(rh) + 10)
            
            target_rect = QtCore.QRect(int(rx), int(ry), w_fixed, final_h)
            
            # 다른 라벨과 겹치는지 확인하고 밀어내기 (위에서 아래로)
            while True:
                collision = False
                for p in placed_rects:
                    if target_rect.intersects(p):
                        collision = True
                        target_rect.moveTop(p.bottom() + 4)
                if not collision:
                    break
            
            lbl.setGeometry(target_rect)
            placed_rects.append(target_rect)
            
            # 가독성을 위한 그림자 효과 적용
            shadow = QtWidgets.QGraphicsDropShadowEffect(lbl)
            shadow.setBlurRadius(4)
            shadow.setOffset(0, 0)
            shadow.setColor(QtGui.QColor(0, 0, 0, 255))
            lbl.setGraphicsEffect(shadow)
            
            lbl.show()
            self.multi_labels.append(lbl)

        self._relayout()
        self.raise_()


    # ------------------------------
    def paintEvent(self, e: QtGui.QPaintEvent):
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.Antialiasing, False)
        p.fillRect(self.rect(), QtGui.QColor(0, 0, 0, 190))

    def focusOutEvent(self, e: QtGui.QFocusEvent):
        self.close()
        super().focusOutEvent(e)
