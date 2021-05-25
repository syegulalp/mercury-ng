% ssi("Page Head Block SSI")
% insert("Page Head Block")
% ssi("Menu")

<div class="section section-sm container">
<div class="col-lg-9 col-md-9 article-body">
<h1>Archive for {{archive.datefmt(archive.date, '%Y')}}</h1></hr>

% for n in archive.posts_desc:
% insert("Post Description")
% end

% p=archive.previous
% if p:
<h2><a href="/{{p.year}}">See posts from {{p.year}}</a></h2>
% end

</div>
<div class="col-lg-3 col-md-3 article-sidebar">
% ssi("More At Ganriki")
</div>
</div>

% ssi("Page Footer")