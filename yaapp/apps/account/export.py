from django.utils.translation import ugettext as _
import StringIO
import xlwt

def export_excel(qs):
    wb = xlwt.Workbook()
    
    ws = wb.add_sheet(_('Users'))
    line, col = 0, 0
    
    greyBG = xlwt.Pattern()
    greyBG.pattern = greyBG.SOLID_PATTERN
    greyBG.pattern_fore_colour = 3
    
    greyFontStyle = xlwt.XFStyle()
    greyFontStyle.pattern = greyBG
    
    # header line
    headerBG = xlwt.easyxf('pattern: pattern solid, fore_colour yellow;')     
    ws.write(line, col+0, _('Id'), headerBG)
    ws.write(line, col+1, _('Username'), headerBG)
    ws.write(line, col+2, _('Name'), headerBG)
    ws.write(line, col+3, _('Email'), headerBG)
    ws.write(line, col+4, _('Facebook ?'), headerBG)
    ws.write(line, col+5, _('Twitter ?'), headerBG)
    ws.write(line, col+6, _('Yasound ?'), headerBG)
    ws.write(line, col+7, _('Join date'), headerBG)

    line, col = 1, 0
    for user in qs.all():
        facebook_enabled = _('No')
        twitter_enabled = _('No')
        yasound_enabled = _('No')
        
        profile = user.get_profile()
        if profile.facebook_enabled:
            facebook_enabled = _('Yes')
        if profile.twitter_enabled:
            twitter_enabled = _('Yes')
        if profile.yasound_enabled:
            yasound_enabled = _('Yes')
        
        email = user.email
        name = profile.name

        ws.write(line, col+0, user.id, xlwt.easyxf('pattern: pattern solid, fore_colour red;'))
        ws.write(line, col+1, unicode(user.username))
        ws.write(line, col+2, name)
        ws.write(line, col+3, email)
        ws.write(line, col+4, facebook_enabled)
        ws.write(line, col+5, twitter_enabled)
        ws.write(line, col+6, yasound_enabled)
        ws.write(line, col+7, unicode(user.date_joined))

        line = line+1

    output = StringIO.StringIO()
    wb.save(output)
    content = output.getvalue()
    output.close()
    return content    