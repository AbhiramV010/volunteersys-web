"""
    Building the printable shift record PDF
"""
import io
import math
import re
from datetime import date, datetime, timedelta

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.platypus import (BaseDocTemplate, Flowable, Frame, PageTemplate,
                                Paragraph, Spacer, Table, TableStyle)

# Ink on paper: this gets printed and photocopied for hour verification, so it stays monochrome.
INK = colors.HexColor("#141414")
MUTED = colors.HexColor("#6f6f6f")
RULE = colors.HexColor("#111111")
HAIRLINE = colors.HexColor("#dcdcdc")

MARGIN = 0.85 * inch
FOOTER_BAND = 0.85 * inch
TRACKING = 1.5

# Serif for the record itself, sans reserved for labels — the contrast does the signposting.
TITLE = ParagraphStyle("title", fontName="Times-Bold", fontSize=20, leading=23, textColor=INK)
DOCMETA = ParagraphStyle("docmeta", fontName="Helvetica", fontSize=7, leading=10.5,
                         textColor=MUTED, alignment=2)
# Leading matches VALUE so the label and its value share a baseline.
LABEL = ParagraphStyle("label", fontName="Helvetica-Bold", fontSize=6.5, leading=13, textColor=MUTED)
VALUE = ParagraphStyle("value", fontName="Times-Roman", fontSize=10, leading=13, textColor=INK)
SECTION = ParagraphStyle("section", fontName="Helvetica-Bold", fontSize=7, leading=11, textColor=MUTED)
NOTE = ParagraphStyle("note", fontName="Times-Italic", fontSize=8.5, leading=12, textColor=MUTED)
BODY = ParagraphStyle("body", fontName="Times-Roman", fontSize=10, leading=14, textColor=INK)
CAPTION = ParagraphStyle("caption", fontName="Helvetica-Bold", fontSize=6.5, leading=10, textColor=MUTED)


def shift_hours(start, end):
    """Length of a shift in hours, treating an end before the start as an overnight shift."""
    if start is None or end is None:
        return 0.0
    span = datetime.combine(date.min, end) - datetime.combine(date.min, start)
    if span < timedelta(0):
        span += timedelta(days=1)
    return span.total_seconds() / 3600


def _phone(number):
    digits = re.sub(r'\D', '', number or "")
    if len(digits) == 10:
        return "(%s) %s-%s" % (digits[:3], digits[3:6], digits[6:])
    return number or "—"


def _tracked(canv, x, y, text, font, size, colour, tracking=TRACKING):
    """Letterspaced text. Tracking only exists on text objects, not on the canvas."""
    obj = canv.beginText(x, y)
    obj.setFont(font, size)
    obj.setFillColor(colour)
    obj.setCharSpace(tracking)
    obj.textOut(text)
    canv.drawText(obj)


def _tracked_width(text, font, size, tracking=TRACKING):
    return stringWidth(text, font, size) + tracking * len(text)


class HRule(Flowable):
    """A plain horizontal rule — the document is built from rules, not boxes."""

    def __init__(self, width, thickness=0.7, colour=RULE, space_before=0, space_after=0):
        Flowable.__init__(self)
        self.width = width
        self.thickness = thickness
        self.colour = colour
        self.space_before = space_before
        self.space_after = space_after

    def wrap(self, available_width, available_height):
        return self.width, self.thickness + self.space_before + self.space_after

    def draw(self):
        self.canv.setStrokeColor(self.colour)
        self.canv.setLineWidth(self.thickness)
        self.canv.line(0, self.space_after, self.width, self.space_after)


def _draw_wordmark(canv, centre_x, baseline):
    """EZ-Volunteer System, set typographically: serif initials, hairline divider, letterspaced sans."""
    mark, word = "EZ", "VOLUNTEER SYSTEM"
    mark_w = _tracked_width(mark, "Times-Bold", 10, 1.0)
    word_w = _tracked_width(word, "Helvetica", 7.5)
    divider_gap = 7.0
    total = mark_w + divider_gap * 2 + 1 + word_w
    left = centre_x - total / 2

    _tracked(canv, left, baseline, mark, "Times-Bold", 10, INK, 1.0)

    divider_x = left + mark_w + divider_gap
    canv.saveState()
    canv.setStrokeColor(HAIRLINE)
    canv.setLineWidth(0.6)
    canv.line(divider_x, baseline - 1.5, divider_x, baseline + 8)
    canv.restoreState()

    _tracked(canv, divider_x + divider_gap, baseline, word, "Helvetica", 7.5, MUTED)


def _draw_furniture(canv, page_num, page_total, generated, heading):
    width, height = letter
    baseline = MARGIN * 0.62

    canv.saveState()
    canv.setStrokeColor(HAIRLINE)
    canv.setLineWidth(0.6)
    canv.line(MARGIN, baseline + 21, width - MARGIN, baseline + 21)

    canv.setFillColor(MUTED)
    canv.setFont("Helvetica", 6.5)
    canv.drawString(MARGIN, baseline + 1.5, "Generated {0:%d %b %Y, %H:%M}".format(generated))
    canv.drawRightString(width - MARGIN, baseline + 1.5,
                         "Page {0} of {1}".format(page_num, page_total))
    canv.restoreState()

    _draw_wordmark(canv, width / 2, baseline)

    # Continuation pages carry a running head so a loose sheet is still identifiable.
    if page_num > 1:
        canv.saveState()
        canv.setFillColor(MUTED)
        canv.setFont("Times-Italic", 8.5)
        canv.drawString(MARGIN, height - MARGIN + 14, heading)
        canv.drawRightString(width - MARGIN, height - MARGIN + 14, "continued")
        canv.setStrokeColor(HAIRLINE)
        canv.setLineWidth(0.6)
        canv.line(MARGIN, height - MARGIN + 8, width - MARGIN, height - MARGIN + 8)
        canv.restoreState()


class _NumberedCanvas(pdfcanvas.Canvas):
    """Defers every page so the footer can print the true page total."""

    def __init__(self, *args, **kwargs):
        self._generated = kwargs.pop("generated", datetime.now())
        self._heading = kwargs.pop("heading", "")
        super().__init__(*args, **kwargs)
        self._pages = []

    def showPage(self):
        self._pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self._pages)
        for page_num, state in enumerate(self._pages, start=1):
            self.__dict__.update(state)
            _draw_furniture(self, page_num, total, self._generated, self._heading)
            super().showPage()
        super().save()


def _masthead(volunteer, generated, summary, width):
    head = Table([[
        Paragraph("Volunteer Shift Record", TITLE),
        Paragraph("RECORD VS-%04d<br/>%s<br/>%s"
                  % (volunteer.ID, generated.strftime("%d %B %Y"), summary), DOCMETA),
    ]], colWidths=[width * 0.55, width * 0.45])
    head.setStyle(TableStyle([
        ("VALIGN", (0, 0), (0, 0), "BOTTOM"),
        ("VALIGN", (1, 0), (1, 0), "BOTTOM"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return head


def _particulars(volunteer, width):
    """Two label/value pairs per row, with the address given the full measure underneath."""
    rows = [
        [Paragraph("VOLUNTEER", LABEL), Paragraph(volunteer.Fullname.title(), VALUE),
         Paragraph("VOLUNTEER ID", LABEL), Paragraph(str(volunteer.ID), VALUE)],
        [Paragraph("PHONE", LABEL), Paragraph(_phone(volunteer.PhoneNum), VALUE),
         Paragraph("REGISTERED BY", LABEL), Paragraph((volunteer.Admin or "—").title(), VALUE)],
        [Paragraph("ADDRESS", LABEL), Paragraph(volunteer.Address or "—", VALUE), "", ""],
    ]

    label_w = 1.05 * inch
    value_w = (width - 2 * label_w) / 2
    table = Table(rows, colWidths=[label_w, value_w, label_w, value_w])
    table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("SPAN", (1, 2), (3, 2)),
    ]))
    return table


def _shift_table(shifts, total_hours, width):
    head = ["", "DATE", "START", "END", "HOURS", "SIGNED OFF BY"]
    rows = [head]
    for index, shift in enumerate(shifts, start=1):
        rows.append([
            str(index),
            shift.Date.strftime("%d %b %Y") if shift.Date else "—",
            shift.Start.strftime("%H:%M") if shift.Start else "—",
            shift.End.strftime("%H:%M") if shift.End else "—",
            "{0:.2f}".format(shift_hours(shift.Start, shift.End)),
            (shift.Admin or "—").title(),
        ])
    rows.append(["", "Total hours logged", "", "", "{0:.2f}".format(total_hours), ""])

    num_w, time_w, hours_w = 0.3 * inch, 0.72 * inch, 0.72 * inch
    date_w = 1.35 * inch
    widths = [num_w, date_w, time_w, time_w, hours_w, width - num_w - date_w - 2 * time_w - hours_w]
    table = Table(rows, colWidths=widths, repeatRows=1)

    last = len(rows) - 1
    style = [
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 6.5),
        ("TEXTCOLOR", (0, 0), (-1, 0), MUTED),
        ("FONTNAME", (0, 1), (-1, -1), "Times-Roman"),
        ("FONTSIZE", (0, 1), (-1, -1), 9.5),
        ("TEXTCOLOR", (0, 1), (-1, -1), INK),
        ("TEXTCOLOR", (0, 1), (0, -1), MUTED),
        ("FONTSIZE", (0, 1), (0, -1), 8),
        ("ALIGN", (0, 0), (0, -1), "RIGHT"),
        ("ALIGN", (2, 0), (4, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (0, -1), 0),
        ("RIGHTPADDING", (0, 0), (0, -1), 9),
        ("LEFTPADDING", (1, 0), (-1, -1), 0),
        ("RIGHTPADDING", (1, 0), (-2, -1), 12),
        ("RIGHTPADDING", (-1, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, 0), 0),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ("TOPPADDING", (0, 1), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
        # Rules only: one under the column heads, hairlines between entries, one above the total.
        ("LINEBELOW", (0, 0), (-1, 0), 0.7, RULE),
        ("LINEBELOW", (0, 1), (-1, last - 2), 0.4, HAIRLINE),
        ("LINEABOVE", (0, last), (-1, last), 0.7, RULE),
        ("FONTNAME", (1, last), (1, last), "Helvetica-Bold"),
        ("FONTSIZE", (1, last), (1, last), 6.5),
        ("TEXTCOLOR", (1, last), (1, last), MUTED),
        ("FONTNAME", (4, last), (4, last), "Times-Bold"),
        ("FONTSIZE", (4, last), (4, last), 11),
        ("TOPPADDING", (0, last), (-1, last), 8),
        ("VALIGN", (0, last), (-1, last), "BOTTOM"),
    ]
    table.setStyle(TableStyle(style))
    return table


def _signature_block(width):
    column = (width - 0.6 * inch) / 2
    table = Table([[" ", "", " "], ["AUTHORISED SIGNATURE", "", "DATE"]],
                  colWidths=[column, 0.6 * inch, column], rowHeights=[30, 12])
    table.setStyle(TableStyle([
        ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 1), (-1, 1), 6.5),
        ("TEXTCOLOR", (0, 1), (-1, 1), MUTED),
        ("LINEABOVE", (0, 1), (0, 1), 0.6, RULE),
        ("LINEABOVE", (2, 1), (2, 1), 0.6, RULE),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 1), (-1, 1), 4),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return table


def build_shift_report(volunteer, shifts):
    """Render the volunteer's full shift history and return the PDF as bytes."""
    generated = datetime.now()
    buffer = io.BytesIO()
    width = letter[0] - 2 * MARGIN
    name = volunteer.Fullname.title()

    doc = BaseDocTemplate(buffer, pagesize=letter,
                          leftMargin=MARGIN, rightMargin=MARGIN,
                          topMargin=MARGIN, bottomMargin=FOOTER_BAND,
                          title="Volunteer Shift Record - " + name,
                          author="EZ-Volunteer System")
    frame = Frame(MARGIN, doc.bottomMargin, width, letter[1] - MARGIN - doc.bottomMargin,
                  id="body", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([PageTemplate(id="report", frames=[frame])])

    total_hours = sum(shift_hours(shift.Start, shift.End) for shift in shifts)

    if shifts:
        summary = "%d %s · %.2f hours" % (len(shifts), "shift" if len(shifts) == 1 else "shifts", total_hours)
    else:
        summary = "no shifts recorded"

    story = [
        _masthead(volunteer, generated, summary, width),
        Spacer(1, 7),
        HRule(width, thickness=1.1),
        Spacer(1, 9),
        _particulars(volunteer, width),
        Spacer(1, 5),
        HRule(width, thickness=0.4, colour=HAIRLINE),
        Spacer(1, 20),
    ]

    if shifts:
        story.append(_shift_table(shifts, total_hours, width))
        story.append(Spacer(1, 7))
        story.append(Paragraph(
            "Rounded up for reporting: %d hours across %d %s."
            % (int(math.ceil(total_hours)), len(shifts), "shift" if len(shifts) == 1 else "shifts"),
            NOTE))
        # Nothing to attest to on an empty record, so the sign-off block is withheld.
        story.append(Spacer(1, 34))
        story.append(Paragraph("I confirm the hours recorded above are a true account of service given.", BODY))
        story.append(Spacer(1, 16))
        story.append(_signature_block(width))
    else:
        story.append(Paragraph("No shifts have been logged for this volunteer yet.", BODY))

    doc.build(story, canvasmaker=lambda *a, **kw: _NumberedCanvas(
        *a, generated=generated, heading="Volunteer Shift Record — " + name, **kw))
    return buffer.getvalue()
