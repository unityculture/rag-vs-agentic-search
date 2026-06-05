"""產生 3 份中文產品說明書範例 PDF（KINYO 風格家電 / 3C），放到 data/pdfs/。
內容皆為 demo 用虛構資料，非真實產品規格。"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
FONT = "STSong-Light"
OUT = os.path.join(os.path.dirname(__file__), "data", "pdfs")
os.makedirs(OUT, exist_ok=True)

# (檔名, 標題, [(章節, 內容), ...])
DOCS = [
    ("KY-3690-多功能電烤盤.pdf", "KINYO 多功能電烤盤 KY-3690 使用說明書", [
        ("產品規格",
         "型號：KY-3690。額定電壓：110V / 60Hz。額定功率：1200W。烤盤尺寸：35 × 25 公分。"
         "溫度範圍：80°C 至 230°C，五段可調。材質：鋁合金烤盤加不沾塗層，外殼為耐熱 PP。"
         "重量：約 2.4 公斤。顏色：珍珠白、霧灰兩款。"),
        ("包裝內容",
         "主機 ×1、可拆式不沾烤盤 ×1、隔熱手套 ×1、清潔海綿 ×1、使用說明書 ×1、保證卡 ×1。"),
        ("使用方式",
         "第一次使用前，請以濕布擦拭烤盤並完全擦乾。將插頭插入 110V 插座，轉動溫控旋鈕至所需溫度，"
         "指示燈亮起表示加熱中，達到設定溫度後指示燈會熄滅。建議預熱 3 至 5 分鐘後再放上食材。"
         "烹調完成後請先轉至最低溫並拔除插頭，待完全冷卻再清潔。"),
        ("安全注意事項",
         "本產品僅供家庭室內使用。加熱過程中外殼與烤盤溫度高，請勿觸碰金屬部位。"
         "請勿浸泡主機於水中。電源線請勿接觸高溫表面。兒童使用時須有成人陪同。"),
        ("保固條款",
         "本產品自購買日起提供一年保固。保固期間內，非人為因素之故障可享免費維修。"
         "下列情形不在保固範圍：人為摔落、自行拆解、泡水、使用非原廠配件、以及正常耗損之不沾塗層刮痕。"
         "辦理保固需出示保證卡與購買發票。保固維修請聯繫客服或攜至原購買通路。"),
        ("常見問題",
         "問：不沾塗層刮傷還能用嗎？答：輕微刮痕不影響使用，但建議改用木質或矽膠鏟避免持續刮傷。"
         "問：可以用洗碗機清洗烤盤嗎？答：可拆式烤盤可用洗碗機，但主機與電源部位嚴禁進水。"
         "問：通電後不加熱怎麼辦？答：請先確認插座有電、溫控旋鈕已轉離 OFF；若仍無反應請送修。"),
    ]),
    ("KY-FN08-USB循環扇.pdf", "KINYO 桌上型 USB 循環扇 KY-FN08 使用說明書", [
        ("產品規格",
         "型號：KY-FN08。供電方式：USB Type-C，5V / 1A。風速段數：三段（弱 / 中 / 強）。"
         "扇葉直徑：15 公分。可調俯仰角度：0 至 90 度。噪音值：最高約 48 分貝。線長：1.2 公尺。"),
        ("包裝內容", "主機 ×1、Type-C 充電線 ×1、使用說明書 ×1、保證卡 ×1。"),
        ("使用方式",
         "以 Type-C 線連接主機與電源（建議使用 5V / 1A 以上的 USB 變壓器或行動電源）。"
         "按電源鍵開機，每按一次切換風速：弱 → 中 → 強 → 關。手動調整俯仰角度對準出風方向。"),
        ("安全注意事項",
         "請勿將手指或異物伸入扇葉護網。請勿在潮濕環境或浴室使用。"
         "長時間不使用請拔除電源。清潔前務必斷電，並以乾布或微濕布擦拭，切勿沖水。"),
        ("保固條款",
         "本產品保固期為一年，自購買日起算。保固範圍涵蓋非人為之馬達與電路故障。"
         "人為損壞、自行拆機、泡水、線材外力扯斷不在保固內。辦理保固請出示保證卡與發票。"),
        ("常見問題",
         "問：接行動電源可以用嗎？答：可以，輸出 5V / 1A 以上即可。"
         "問：風變小了是什麼原因？答：多為供電不足或扇葉積灰，請改用足瓦數電源並清潔扇葉。"
         "問：可以整台水洗嗎？答：不可以，主機含馬達與電路，僅能以微濕布擦拭。"),
    ]),
    ("KY-PB20-行動電源.pdf", "KINYO 行動電源 20000mAh KY-PB20 使用說明書", [
        ("產品規格",
         "型號：KY-PB20。電池容量：20000mAh（鋰聚合物）。輸入：Type-C 5V/3A、Micro-USB 5V/2A。"
         "輸出：USB-A ×2（5V/2.4A）、Type-C 雙向 5V/3A。支援最大輸出 18W。"
         "充滿時間：約 6 至 7 小時（Type-C）。重量：約 360 公克。"),
        ("包裝內容", "行動電源主機 ×1、Type-C 充電線 ×1、收納袋 ×1、使用說明書 ×1、保證卡 ×1。"),
        ("使用方式",
         "首次使用建議先充滿電。以 Type-C 接電源為主機充電，四顆指示燈顯示電量。"
         "將裝置接上任一輸出孔即自動供電；多數機型支援接上即充，無需按鍵。"
         "搭飛機時請隨身攜帶，勿託運。"),
        ("安全注意事項",
         "請勿置於高溫（超過 45°C）或陽光直曬處。請勿摔落、擠壓或拆解。"
         "若機身鼓起、發燙或有異味請立即停止使用。請使用合規格的充電線材。"),
        ("保固條款",
         "本產品提供一年保固。電芯容量自然衰退屬正常現象，不列入保固。"
         "人為摔損、進水、自行拆解、鼓包因外力造成者不在保固範圍。"
         "保固期內非人為之充放電異常可送修，需檢附保證卡與購買憑證。"),
        ("常見問題",
         "問：可以邊充邊放嗎？答：支援，但邊充邊放會發熱且效率較低，不建議長時間如此使用。"
         "問：充不滿電怎麼辦？答：請改用 5V/3A 的 Type-C 電源，並確認線材支援該電流。"
         "問：可以帶上飛機嗎？答：20000mAh 約 74Wh，多數航空可隨身攜帶，請勿託運並依航空規定。"),
    ]),
]


def build():
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=styles["Title"], fontName=FONT, fontSize=18, leading=24)
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontName=FONT, fontSize=13, leading=18,
                        spaceBefore=10, spaceAfter=4, textColor="#0F1E3D")
    body = ParagraphStyle("body", parent=styles["BodyText"], fontName=FONT, fontSize=11, leading=18,
                          alignment=TA_LEFT)
    for fname, title, sections in DOCS:
        path = os.path.join(OUT, fname)
        doc = SimpleDocTemplate(path, pagesize=A4, topMargin=20*mm, bottomMargin=18*mm,
                                leftMargin=20*mm, rightMargin=20*mm, title=title)
        story = [Paragraph(title, h1), Spacer(1, 6)]
        for sec, text in sections:
            story.append(Paragraph(sec, h2))
            story.append(Paragraph(text, body))
        doc.build(story)
        print("wrote", path)


if __name__ == "__main__":
    build()
