% from cms.models import Tag
% c = load("code_module")
% ssi("Page Head Block SSI")
% insert("Page Head Block")
% ssi("Menu")

<div class="section section-sm container">
<div class="col-lg-9 col-md-9 article-body">

% tag_txt, tag_link = c.tag_fmt(archive.tag)
<h1>{{tag_txt[0]}}</h1><hr/>

% tag_listing = archive.blog.tags.where(Tag.title ** f'{tag_txt[0]}:%').order_by(Tag.title.asc())
% for t in tag_listing:
% tx = t.title.split(':',1)[1]
% tl = t.basename.split('-',1)
<h2><a href="/{{tl[0]}}/{{tl[1]}}">{{tx}}</h2>
% end
<hr/>

</div>
    <div class="col-lg-3 col-md-3 article-sidebar">
        % ssi("More At Ganriki")
    </div>
</div>

% ssi("Page Footer")

