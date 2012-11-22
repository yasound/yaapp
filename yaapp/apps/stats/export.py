from django.utils.translation import ugettext as _
import StringIO
import xlwt
from models import RadioListeningStat

def format_seconds(sec):
     q,s=divmod(sec,60)
     h,m=divmod(q,60)
     return "%02d:%02d:%02d" %(h,m,s)

def export_radio_stats(radio, days=30*6):
    wb = xlwt.Workbook()

    ws = wb.add_sheet(_('Radio'))
    line, col = 0, 0

    greyBG = xlwt.Pattern()
    greyBG.pattern = greyBG.SOLID_PATTERN
    greyBG.pattern_fore_colour = 3

    greyFontStyle = xlwt.XFStyle()
    greyFontStyle.pattern = greyBG
    xf_date = xlwt.easyxf(num_format_str='DD/MM/YYYY')
    # header line
    headerBG = xlwt.easyxf('pattern: pattern solid, fore_colour yellow;')
    ws.write(line, col + 0, _('Date'), headerBG)
    ws.write(line, col + 1, _('Overall listening time'), headerBG)
    ws.write(line, col + 2, _('Audience peak'), headerBG)
    ws.write(line, col + 3, _('Connections'), headerBG)
    ws.write(line, col + 4, _('Favorites'), headerBG)
    ws.write(line, col + 5, _('Likes'), headerBG)
    ws.write(line, col + 6, _('Dislikes'), headerBG)

    line, col = 1, 0
    for stat in RadioListeningStat.objects.daily_stats(radio, days):
        ws.write(line, col + 0, stat.date, xf_date)
        ws.write(line, col + 1, format_seconds(stat.overall_listening_time))
        ws.write(line, col + 2, stat.audience_peak)
        ws.write(line, col + 3, stat.connections)
        ws.write(line, col + 4, stat.favorites)
        ws.write(line, col + 5, stat.likes)
        ws.write(line, col + 6, stat.dislikes)

        line = line + 1

    output = StringIO.StringIO()
    wb.save(output)
    content = output.getvalue()
    output.close()
    return content
