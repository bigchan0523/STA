from googletrans import Translator

SRC_LANG = {
    'zh-CN' : 'zh-cn',
    'en-US' : 'en',
    'ja-JP' : 'ja'
}

class googleClient:
    def __init__(self):
        self.trs = Translator()
    
    def translate(self, ocr_text: str, src: str) -> str:
        """
        OCR 텍스트를 받아 번역 결과 문자열을 반환.
        """
        if not isinstance(ocr_text, str):
            raise TypeError("ocr_text는 문자열이어야 합니다.")
        # lang = self.trs.detect(ocr_text).lang
        res = self.trs.translate(ocr_text, src=SRC_LANG[src], dest='ko')
        return res.text