from django.utils.translation import ugettext as _
import StringIO
import xlwt

def export_promocodes_excel(qs):
    wb = xlwt.Workbook()

    ws = wb.add_sheet(_('Promocode'))
    line, col = 0, 0

    greyBG = xlwt.Pattern()
    greyBG.pattern = greyBG.SOLID_PATTERN
    greyBG.pattern_fore_colour = 3

    greyFontStyle = xlwt.XFStyle()
    greyFontStyle.pattern = greyBG

    # header line
    headerBG = xlwt.easyxf('pattern: pattern solid, fore_colour yellow;')
    ws.write(line, col+0, _('Code'), headerBG)
    line, col = 1, 0
    for item in qs.all():

        ws.write(line, col+0, item.code)

        line = line+1

    output = StringIO.StringIO()
    wb.save(output)
    content = output.getvalue()
    output.close()
    return content
