#!python
from cms.models import Media
import regex as re

tag_colors={'title':'success','demographic':'info','meta':'primary','people':'danger'}

topic_headers={
'@kickstarter':'''
<div class="alert alert-warning">
<b>Note:</b> The item discussed in this review was made available by way of a Kickstarter fund. The author of this piece helped fund the completion of that project.
</div>
''',
'@spoiler':'''
<div class="alert alert-danger">
<b>Warning:</b> This article contains <b>major spoilers.</b>
</div>
''',
'meta: Let\'s Film This':'''
<div data-header="meta-lets-film-this" class="alert alert-success">
<a href="/meta/lets-film-this"><b>Let's Film This</b></a> is an ongoing series where we explore the idea of adapting different anime as live-action productions: what it would take, which shows would make for the best adaptations, and what issues would be raised in the translation.
</div>
''',
'meta: Let\'s Animate This':'''
<div data-header="meta-lets-animate-this" class="alert alert-success">
<a href="/meta/lets-animate-this"><b>Let's Animate This</b></a> is an ongoing series where we explore the idea of adapting non-anime properties as anime productions: what it would take, which works would make for the best adaptations, and what issues would be raised in the translation.
</div>
''',
'meta: Short Takes':'''
<div data-header="meta-short-takes" class="alert alert-success">
<a href="/meta/short-takes"><b>Short Takes</b></a> looks at newly released products for ongoing titles, a way for us to examine a series in progress outside of a full-length critical piece.
</div>
''',
'meta: Characters Of Distinction':'''
<div data-header="meta-characters-of-distinction" class="alert alert-success">
<a href="/meta/characters-of-distinction"><b>Characters Of Distinction</b></a> is an ongoing series where we examine the most noteworthy and memorable characters of anime: why we're drawn to them, what makes them great, and how they influence other creations beyond them.
</div>
''',}

topic_footers={'@promo':'''
<div class="alert alert-info">
<b>Note:</b> This product was provided by the creator or publisher
as a promotional item for the sake of a review.
</div>
''',
'@purchased':'''
<div class="alert alert-info">
<b>Note:</b> The products mentioned here were purchased by the reviewer with personal
funds, or watched using the reviewer's personal streaming account.
No compensation was provided by the creators or publishers
for the sake of this review. 
</div>
'''}

topic_headers={
'@kickstarter':'''
<div class="alert alert-warning">
<b>Note:</b> The item discussed in this review was made available by way of a Kickstarter fund. The author of this piece helped fund the completion of that project.
</div>
''',
'@spoiler':'''
<div class="alert alert-danger">
<b>Warning:</b> This article contains <b>major spoilers.</b>
</div>
''',
'meta: Let\'s Film This':'''
<div data-header="meta-lets-film-this" class="alert alert-success">
<a href="/meta/lets-film-this"><b>Let's Film This</b></a> is an ongoing series where we explore the idea of adapting different anime as live-action productions: what it would take, which shows would make for the best adaptations, and what issues would be raised in the translation.
</div>
''',
'meta: Let\'s Animate This':'''
<div data-header="meta-lets-animate-this" class="alert alert-success">
<a href="/meta/lets-animate-this"><b>Let's Animate This</b></a> is an ongoing series where we explore the idea of adapting non-anime properties as anime productions: what it would take, which works would make for the best adaptations, and what issues would be raised in the translation.
</div>
''',
'meta: Short Takes':'''
<div data-header="meta-short-takes" class="alert alert-success">
<a href="/meta/short-takes"><b>Short Takes</b></a> looks at newly released products for ongoing titles, a way for us to examine a series in progress outside of a full-length critical piece.
</div>
''',
'meta: Characters Of Distinction':'''
<div data-header="meta-characters-of-distinction" class="alert alert-success">
<a href="/meta/characters-of-distinction"><b>Characters Of Distinction</b></a> is an ongoing series where we examine the most noteworthy and memorable characters of anime: why we're drawn to them, what makes them great, and how they influence other creations beyond them.
</div>
''',}

default_copyright = "[No copyright information specified]"

def get_copyright(url):    
    url = url.replace(f"https://www.ganriki.org/media/","")
    try:
        img = Media.get(
            filepath = url,
            blog = archive.blog
        )
    except:
        return default_copyright
    meta = img.get_metadata('copyright')
    if not meta:
        return default_copyright
    return meta.value

    
def get_img(post):

    main_img_meta = post.get_metadata('img')
    if main_img_meta is None:
        main_img = Media.get(filepath='2013/totoro-01.jpg')
    else:
        main_img = Media.get_by_id(int(main_img_meta.value))
    
    main_img_copyright = main_img.get_metadata('copyright')
    if main_img_copyright is None:
        main_img_copyright = default_copyright
    else:
        main_img_copyright = main_img_copyright.value

    main_img_position = main_img.get_metadata('position')
    if main_img_position is None:
        main_img_position = 0
    else:
        main_img_position = main_img_position.value
        
    return main_img, main_img_copyright, main_img_position


replace=[
    ['<a href=.search:([^\'"]*).[^>]*?>',
    r'<a target="_blank" href="https://google.com/search?q=\1%20site:ganriki.org">'],
    ['<a href=.google:([^\'"]*).[^>]*?>',
    r'<a target="_blank" href="https://google.com/search?q=\1">'],
    ['<a href=.amazon.com:([^\'"]*).[^>]*?>',r'<a href="https://www.amazon.com/dp/\1?tag=thegline">'],
    [r'\&nbsp;',' '],
    [r' -- ',' &mdash; '],
    #[r'([$ ,;])"',r'\1“'],
    #[r'"([\,\.\!\? ])',r'”\1'],
]

for n in replace:
    n[0]=re.compile(n[0])

re_excerpt = re.compile(r'<p class=.lead.[^>]*?>(.*?)</p>.*',re.DOTALL)
      
caption = re.compile('''<div class=['"]([^'"]*?)['"][^>]*?>[^<]*?<img [^>]*?src=["']([^'"]*?)['"][^>]*?>[^<]*?<img [^>]*?src=['"]([^'"]*?)['"][^>]*?>[^<]*?<p>(.*?)</p>[^<]*?</div>''',re.DOTALL)

single_caption = re.compile('''<div class=['"]([^'"]*?)['"][^>]*?>\s*?<img [^>]*?src=["']([^'"]*?)['"][^>]*?>\s*?<p>(.*?)</p>\s*?</div>''',re.DOTALL)

replacement = r'<figure class="\1"><a href="\2" data-toggle="lightbox"><img alt="\2" class="lazy" src="/media/gray.png" data-original="\2"/></a>&nbsp;<a href="\3" data-toggle="lightbox"><img alt="\3" class="lazy" src="/media/gray.png" data-original="\3"/></a><figcaption><span class="copyright">{}</span><br/>\4</figcaption></figure>'

single_replacement = r'<figure class="\1"><div class="c-fix"><span class="img-caption-sm disable-text">{}</span><a href="\2" data-toggle="lightbox"><img alt="\2" class="lazy" src="/media/gray.png" data-original="\2"/></a></div><figcaption>\3</figcaption></figure>'

amazon = re.compile(r'''<p>(.*?)<a href=['"](left|right).amazon.com:([^'"]*?)['"][^>]*?>(.*?)</a>(.*?)</p>''')

amazon_replacement = r'''
<div class="pclear-\2">
<div style="text-align: center" class="well well-sm pull-\2 float-\2"><a title="Click here to purchase this item. Purchases support this site." target="_blank" rel="nofollow" href="http://www.amazon.com:/dp/\3/?tag=thegline"><img alt="Amazon \3" class="bx" src="http://images.amazon.com/images/P/\3.01._SS150_LZZZZZZZ.jpg"/></a><br/><span style="font-size: .66em">Purchases support this site.</span></div>
<p>\1<a href="http://www.amazon.com/dp/\3?tag=thegline">\4</a>\5</p></div>
'''

# Image caption regex
def replace_text(text):
    for cap,rep in ((single_caption,single_replacement),(caption,replacement)):
        for match in cap.finditer(text):
            img_copyright = get_copyright(match.group(2))
            text = cap.sub(rep.format(img_copyright), text, count=1)

    for match in amazon.finditer(text):
        text = amazon.sub(amazon_replacement, text, count=1)

    for n in replace:
        text=n[0].sub(n[1],text)

    return text

def tag_fmt(tag):
    tag_txt = tag.title.split(':',1)
    tag_link = tag.basename.split('-',1)
    return tag_txt, tag_link