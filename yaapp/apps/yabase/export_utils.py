from django.utils.translation import ugettext as _
import StringIO
import xlwt

def export_pur(songs):
    wb = xlwt.Workbook()
    
    ws = wb.add_sheet(_('Songs'))
    line, col = 0, 0
    
    greyBG = xlwt.Pattern()
    greyBG.pattern = greyBG.SOLID_PATTERN
    greyBG.pattern_fore_colour = 3
    
    greyFontStyle = xlwt.XFStyle()
    greyFontStyle.pattern = greyBG
    
    # header line
    headerBG = xlwt.easyxf('pattern: pattern solid, fore_colour yellow;')     
    ws.write(line, col+0, _('Name'), headerBG)
    ws.write(line, col+1, _('Artist'), headerBG)

    line, col = 1, 0
    for item in songs:
        name = item.get('name')
        artist = item.get('artist')
        if len(artist) <= 0:
            continue
        if 'piste' in artist.lower():
            continue
        if 'track' in name.lower():
            continue

        ws.write(line, col+0, name)
        ws.write(line, col+1, artist)

        line = line+1

    output = StringIO.StringIO()
    wb.save(output)
    content = output.getvalue()
    output.close()
    return content    