import sys
import warnings
warnings.filterwarnings("ignore") # google.generativeai 등에서 발생하는 경고 메시지 무시

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import Qt
# UI 및 설정 관련 모듈만 먼저 로드
from ui_app import MainWindow
from hotkey_manager import WinHotkeyManager
from settings import SettingsManager

def capture_rect_global(rect):
    import mss
    from PIL import Image
    with mss.mss() as sct:
        raw = sct.grab({"left": rect.x(), "top": rect.y(),
                        "width": rect.width(), "height": rect.height()})
        return Image.frombytes("RGB", (raw.width, raw.height), raw.rgb)

def _prefix_function(s: str) -> list[int]:
    pi = [0] * len(s)
    j = 0
    for i in range(1, len(s)):
        while j and s[i] != s[j]:
            j = pi[j - 1]
        if s[i] == s[j]:
            j += 1
            pi[i] = j
    return pi

class App(QtWidgets.QApplication):
    pass

def main():
    app = App(sys.argv)

    # 1) 설정 로드
    mgr = SettingsManager()
    w = MainWindow(mgr)
    w.setWindowIcon(QtGui.QIcon("icon.ico"))
    w.show()

    # LLM 클라이언트는 나중에 필요할 때 생성
    llm = None

    # overlay
    w.current_overlay = None

    # 2) OCR 연결
    before_ocr_text = None
    def run_pipeline(rect_global):
        nonlocal before_ocr_text
        from ocr_win import windows_ocr
        from overlay import OverlayWindow
        from translate_api.llm_api import LLMClient, LLMError
        from translate_api.google_api import googleClient
        from clipboard import copy_img, copy_text

        if getattr(w, "current_overlay", None):
            try: w.current_overlay.close()
            except Exception: pass
            w.current_overlay = None

        # 캡처/OCR/번역
        try:
            img = capture_rect_global(rect_global)
            if mgr.copy_rule == 2: copy_img(img)
            ocr_data = windows_ocr(img, w.get_lang_tag()) # 리스트 반환 [{text, rect}, ...]
            if not ocr_data:
                return
            
            # --- [지능형 그룹화 전처리] ---
            blocks = []
            if ocr_data:
                current_block = [ocr_data[0]]
                for next_item in ocr_data[1:]:
                    prev_item = current_block[-1]
                    dist = next_item["rect"][1] - (prev_item["rect"][1] + prev_item["rect"][3])
                    line_h = prev_item["rect"][3]
                    
                    # 인접하고 문장부호가 없으면 같은 블록(문장)으로 병합
                    if dist < line_h * 1.5 and not prev_item["text"].strip().endswith(('.', '!', '?')):
                        current_block.append(next_item)
                    else:
                        blocks.append(current_block)
                        current_block = [next_item]
                blocks.append(current_block)
            
            # 블록별 원문 텍스트 생성 (줄바꿈 대신 공백으로 합쳐서 문맥 유지)
            block_texts = [" ".join(it["text"] for it in b) for b in blocks]
            ocr_text_for_llm = "\n".join(block_texts)
            # ---------------------------

        except Exception as e:
            w.show_text(f"OCR 실패: {e}")
            return
        
        if mgr.copy_rule == 0: copy_text(ocr_text_for_llm)
        if mgr.no_llm:
            w.show_text(ocr_text_for_llm)
            return
        
        # 오버레이 생성
        overlay = None
        if mgr.use_overlay_layout:
            overlay = OverlayWindow(rect_global, "", font_family=mgr.font_family, font_size=mgr.font_size)
            w.current_overlay = overlay
        
        try:
            w.show_text("번역 중...")
            QtWidgets.QApplication.processEvents() # 번역 진입 전 화면 업데이트 
            
            translated = None
            if mgr.use_google_api: translated = googleClient().translate(ocr_text=ocr_text_for_llm, src=w.get_lang_tag())
            else: translated = LLMClient(mgr).translate(ocr_text_for_llm)
            
            if mgr.use_overlay_layout:
                # 블록별 번역 결과 매칭
                trans_blocks = translated.split('\n')
                final_data = []
                
                for i, block in enumerate(blocks):
                    t_block = trans_blocks[i] if i < len(trans_blocks) else ""
                    
                    # 블록 전체 영역(Union Rect) 구하기
                    bx = min(it["rect"][0] for it in block)
                    by = min(it["rect"][1] for it in block)
                    bw = max(it["rect"][0] + it["rect"][2] for it in block) - bx
                    bh = max(it["rect"][1] + it["rect"][3] for it in block) - by
                    
                    final_data.append({
                        "text": t_block,
                        "rect": (bx, by, bw, bh)
                    })
                overlay.set_multi_text(final_data)
                
            original_full = "\n".join(item["text"] for item in ocr_data)
            w.show_text(translated + f"\n\n\n### 캡처한 원문:\n{original_full}")
            if mgr.copy_rule == 1: copy_text(translated)
        except LLMError as e:
            w.show_text(f"번역 실패: {e}")


    def on_rect_selected(rect_global):
        w.last_selection_rect = QtCore.QRect(rect_global)
        run_pipeline(rect_global)

    w.rectSelected.connect(on_rect_selected)

    # 3) 전역 핫키 등록
    before_hk_key = None
    before_hk_rem_key = None
    hk = None
    hk_rem = None
    def register_hotkey():
        nonlocal hk, hk_rem, before_hk_key, before_hk_rem_key
        ok1 = True
        ok2 = True
        # hotkey 1
        if before_hk_key != mgr.hotkey_combo and mgr.hotkey_combo: 
            ok1 = None
            if hk is not None:
                hk.stop(); hk = None

            def on_hotkey():
                QtCore.QMetaObject.invokeMethod(w, "start_capture", Qt.QueuedConnection)

            hk = WinHotkeyManager(on_hotkey, combo=mgr.hotkey_combo, norepeat=True, hotkey_id=1)
            ok1 = hk.start()
            before_hk_key = mgr.hotkey_combo

        # hotkey 2
        if before_hk_rem_key != mgr.hotkey_rem_combo and mgr.hotkey_rem_combo: 
            ok2 = None
            if hk_rem is not None:
                hk_rem.stop(); hk_rem = None

            def on_hotkey_rem():
                QtCore.QMetaObject.invokeMethod(w, "run_last_rect", Qt.QueuedConnection)

            hk_rem = WinHotkeyManager(on_hotkey_rem, combo=mgr.hotkey_rem_combo, norepeat=True, hotkey_id=2)    
            ok2 = hk_rem.start()
            before_hk_rem_key = mgr.hotkey_rem_combo

        # post processing
        if ok1 and ok2:
            w.statusBar().showMessage(f"전역 핫키 등록: {mgr.hotkey_combo}, {mgr.hotkey_rem_combo}", 4000)
        else:
            reason = hk.last_error if hk else "알 수 없는 오류"
            if not reason and hk_rem: reason = hk_rem.last_error
            w.statusBar().showMessage(f"전역 핫키 등록 실패: {reason}", 6000)
            QtWidgets.QMessageBox.warning(w, "핫키 등록 실패", f"핫키 등록 실패:{reason}")
    register_hotkey()

    # 4) 설정 저장
    def on_settings_updated():
        from translate_api.llm_api import LLMClient
        mgr.load()
        register_hotkey()   # 새 조합으로 재등록
        # LLM 클라이언트 재구성 (필요한 경우만)
        # nonlocal llm; llm = LLMClient(mgr) 
        
    w.settingsUpdated.connect(on_settings_updated)

    app.aboutToQuit.connect(lambda: (hk and hk.stop(), hk_rem and hk_rem.stop()))
    sys.exit(app.exec_())

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        with open("crash_log.txt", "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        raise
