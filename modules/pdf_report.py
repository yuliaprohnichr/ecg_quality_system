from datetime import datetime

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


pdfmetrics.registerFont(TTFont("DejaVu", "DejaVuSans.ttf"))

DARK = colors.HexColor("#06111F")
NAVY = colors.HexColor("#0B2A4A")
BLUE = colors.HexColor("#00AEEF")
LIGHT = colors.HexColor("#F4F8FC")
TEXT = colors.HexColor("#111827")
MUTED = colors.HexColor("#64748B")


def p(text, style):
    return Paragraph(str(text), style)


def generate_pdf_report(metrics, conclusion, plot_images=None, filename="ecg_report.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=1.1 * cm,
        leftMargin=1.1 * cm,
        topMargin=1.0 * cm,
        bottomMargin=1.0 * cm
    )

    styles = getSampleStyleSheet()

    title = ParagraphStyle(
        "title",
        parent=styles["Title"],
        fontName="DejaVu",
        fontSize=22,
        textColor=colors.white,
        leading=26
    )

    subtitle = ParagraphStyle(
        "subtitle",
        parent=styles["BodyText"],
        fontName="DejaVu",
        fontSize=8,
        textColor=colors.HexColor("#BFD7FF"),
        leading=11
    )

    h2 = ParagraphStyle(
        "h2",
        parent=styles["Heading2"],
        fontName="DejaVu",
        fontSize=12,
        textColor=NAVY,
        spaceBefore=8,
        spaceAfter=6
    )

    body = ParagraphStyle(
        "body",
        parent=styles["BodyText"],
        fontName="DejaVu",
        fontSize=8,
        textColor=TEXT,
        leading=11
    )

    white = ParagraphStyle(
        "white",
        parent=styles["BodyText"],
        fontName="DejaVu",
        fontSize=8,
        textColor=colors.white,
        leading=11
    )

    elements = []
    date_text = datetime.now().strftime("%d.%m.%Y %H:%M")

    header = Table(
        [[
            p("<b>ECG QUALITY<br/>ANALYSIS REPORT</b>", title),
            p(f"<b>Дата та час аналізу</b><br/>{date_text}", subtitle)
        ]],
        colWidths=[11.5 * cm, 5.0 * cm],
        rowHeights=[2.6 * cm]
    )

    header.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), DARK),
        ("LINEBELOW", (0, 0), (-1, -1), 4, BLUE),
        ("BOX", (0, 0), (-1, -1), 1, DARK),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("PADDING", (0, 0), (-1, -1), 14),
    ]))

    elements.append(header)
    elements.append(Spacer(1, 10))

    quality = metrics.get("Оцінка якості", "Невідомо")

    about_card = Table(
        [[
            p(
                "<b>ПРО СИСТЕМУ</b><br/><br/>"
                "Інформаційна система виконує автоматизовану обробку "
                "ЕКГ-сигналу, розрахунок індикаторів якості, визначення "
                "R-піків, оцінювання ЧСС та формування підсумкового висновку.",
                body
            ),
            p(
                f"<b>ПІДСУМКОВА ОЦІНКА ЯКОСТІ</b><br/><br/>"
                f"<font size='22' color='#22C55E'>A</font><br/>"
                f"<font color='#22C55E'><b>{quality}</b></font>",
                white
            )
        ]],
        colWidths=[8.0 * cm, 8.5 * cm],
        rowHeights=[3.0 * cm]
    )

    about_card.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), colors.white),
        ("BACKGROUND", (1, 0), (1, 0), NAVY),
        ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#D8E3EF")),
        ("INNERGRID", (0, 0), (-1, -1), 0.6, colors.HexColor("#E2E8F0")),
        ("PADDING", (0, 0), (-1, -1), 14),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))

    elements.append(about_card)
    elements.append(Spacer(1, 10))

    elements.append(p("<b>КЛЮЧОВІ ПОКАЗНИКИ</b>", h2))

    key_cards = [
        ("Кількість відліків", metrics.get("Кількість відліків", "-")),
        ("Частота", metrics.get("Частота дискретизації", "-")),
        ("R-піки", metrics.get("Кількість знайдених R-піків", "-")),
        ("ЧСС", metrics.get("Орієнтовна ЧСС", "-")),
        ("RR", metrics.get("Середній RR-інтервал", "-")),
    ]

    cards = Table(
        [[p(f"<b><font color='#0B2A4A'>{value}</font></b><br/><font color='#64748B'>{name}</font>", body)
          for name, value in key_cards]],
        colWidths=[3.25 * cm] * 5,
        rowHeights=[1.45 * cm]
    )

    cards.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#D8E3EF")),
        ("INNERGRID", (0, 0), (-1, -1), 0.6, colors.HexColor("#E2E8F0")),
        ("PADDING", (0, 0), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))

    elements.append(cards)
    elements.append(Spacer(1, 12))

    elements.append(p("<b>ДЕТАЛЬНІ ІНДИКАТОРИ ЯКОСТІ</b>", h2))

    items = list(metrics.items())
    half = (len(items) + 1) // 2
    left = items[:half]
    right = items[half:]

    table_data = [[
        p("<b>Показник</b>", white),
        p("<b>Значення</b>", white),
        p("<b>Показник</b>", white),
        p("<b>Значення</b>", white),
    ]]

    for i in range(max(len(left), len(right))):
        l_key, l_val = left[i] if i < len(left) else ("", "")
        r_key, r_val = right[i] if i < len(right) else ("", "")

        table_data.append([
            p(l_key, body), p(l_val, body),
            p(r_key, body), p(r_val, body),
        ])

    details = Table(table_data, colWidths=[4.2 * cm, 3.7 * cm, 4.2 * cm, 3.7 * cm])

    details.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("LINEBELOW", (0, 0), (-1, 0), 2, BLUE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D6E0EA")),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))

    elements.append(details)
    elements.append(Spacer(1, 12))

    conclusion_card = Table(
        [[p("<b>ВИСНОВОК</b><br/><br/>" + conclusion, body)]],
        colWidths=[16.5 * cm]
    )

    conclusion_card.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EEF7FF")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#B8DDF5")),
        ("LINELEFT", (0, 0), (0, -1), 5, BLUE),
        ("PADDING", (0, 0), (-1, -1), 12),
    ]))

    elements.append(conclusion_card)

    if plot_images:
        elements.append(PageBreak())
        elements.append(header)
        elements.append(Spacer(1, 12))
        elements.append(p("<b>ВІЗУАЛІЗАЦІЯ РЕЗУЛЬТАТІВ АНАЛІЗУ</b>", h2))

        for title_text, key in [
            ("Фрагмент обробленого ЕКГ-сигналу", "ecg_fragment"),
            ("Виявлення R-піків", "r_peaks"),
            ("Спектральний аналіз сигналу", "spectrum"),
        ]:
            if key in plot_images:
                elements.append(p(f"<b>{title_text}</b>", h2))
                img = Image(plot_images[key], width=16.3 * cm, height=6.2 * cm)
                elements.append(img)
                elements.append(Spacer(1, 10))

    footer = Table(
        [[
            p("ECG QUALITY ANALYSIS SYSTEM", subtitle),
            p("Автоматизований аналіз та візуалізація індикаторів якості сигналів ЕКГ", subtitle)
        ]],
        colWidths=[6.0 * cm, 10.5 * cm],
        rowHeights=[0.8 * cm]
    )

    footer.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), DARK),
        ("LINEABOVE", (0, 0), (-1, -1), 2, BLUE),
        ("PADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))

    elements.append(footer)

    doc.build(elements)

    return filename