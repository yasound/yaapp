from django.http import HttpResponse

def song_graph(request, radio_id, song_id):
    YASOUND_APP_ID = '296167703762159'
    YASOUND_NAMESPACE = 'yasound'
    
    code = ''
    
    code += '<html xmlns="http://www.w3.org/1999/xhtml" dir="ltr" lang="en-US" xmlns:fb="https://www.facebook.com/2008/fbml">'

    code += '<head prefix="og: http://ogp.me/ns# fb: http://ogp.me/ns# %s: http://ogp.me/ns/apps/%s#">' % (YASOUND_NAMESPACE, YASOUND_NAMESPACE)
    code += '<meta property="fb:app_id" content="%s" />' % YASOUND_APP_ID
    code += '<meta property="og:type" content="%s:song" />' % YASOUND_NAMESPACE 
    code += '<meta property="og:title" content="Stuffed Cookies" />'
    code += '<meta property="og:image" content="http://example.com/zhen/cookie.jpg" />' 
    code += '<meta property="og:description" content="The Turducken of Cookies" />'
    code += '<meta property="og:url" content="https://dev.yasound.com/graph/radio/%d/song/%d">' % (int(radio_id), int(song_id)) 
    code += '</head>'

    code += '<body>' 
    code += '<div id="fb-root"></div>'
    code += '<script src="http://connect.facebook.net/en_US/all.js"></script>'
    code += '<script>'
    code += 'FB.init({' 
    code += "appId:'%s', cookie:true," % YASOUND_APP_ID 
    code += 'status:true, xfbml:true, oauth:true'
    code += '});'
    code += '</script>'

    code += '<fb:add-to-timeline></fb:add-to-timeline>'

    code += '<h3>'
    code += '<font size="30" face="verdana" color="grey">'
    code += 'Stuffed Cookies'
    code += '</font>'
    code += '</h3>'
    code += '<p>'
    code += '<img title="Stuffed Cookies"' 
    code += 'src="http://fbwerks.com:8000/zhen/cookie.jpg"' 
    code += 'width="550"/><br />'
    code += '</p>'
    code += '</body>' 
    code += '</html>'
    
    return HttpResponse(code)
