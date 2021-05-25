% c = load("code_module")
% ssi("Page Head Block SSI")
% insert("Page Head Block")
% ssi("Menu")

<div class="section section-sm container">
<div class="col-lg-9 col-md-9 article-body">

% tag_txt, tag_link = c.tag_fmt(archive.tag)
<h1><a href="/{{tag_link[0]}}">{{tag_txt[0]}}</a>: {{tag_txt[1]}}</h1><hr/>

% for n in archive.posts_desc:
% insert("Post Description")
% end
<hr/>
% p=archive.previous
% if p:
<h2><a href="../{{p.year}}">See <b>{{tag_txt[1]}}</b> posts from {{p.year}}</a></h2>
% end

</div>
    <div class="col-lg-3 col-md-3 article-sidebar">
        % ssi("More At Ganriki")
    </div>
</div>

% ssi("Page Footer")

