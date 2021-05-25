% c = load("code_module")
% ssi("Page Head Block SSI")
% insert("Page Head Block")
% ssi("Menu")

<div class="section section-sm container">
<div class="col-lg-9 col-md-9 article-body">

% year = 0
% tag_txt, tag_link = c.tag_fmt(archive.tag)
<h1><a href="/{{tag_link[0]}}">{{tag_txt[0]}}</a>: {{tag_txt[1]}}</h1><hr/>

% for n in archive.posts_desc.limit(20):

% if n.date_published.year != year:
% year = n.date_published.year
<h3><a href="{{year}}">{{year}}</a></h3><hr/>
% end

% insert("Post Description")

% end
<hr/>
<h2>See more <b>{{tag_txt[1]}}</b> posts from <a href="{{year}}">{{year}}</a></h2>
<hr/>

</div>
    <div class="col-lg-3 col-md-3 article-sidebar">
        % ssi("More At Ganriki")
    </div>
</div>

% ssi("Page Footer")

