% ssi("Page Head Block SSI")
% insert("Page Head Block")
% ssi("Menu")

<div class="section section-sm container">
<div class="col-lg-9 col-md-9 article-body">

<h1><a href="/{{archive.category.basename}}">{{archive.category.title}}</a> Archives: {{archive.year}}</h1><hr/>

% for n in archive.posts_desc:
% insert("Post Description")
% end

<hr/>
% p=archive.previous
% if p:
<h2><a href="/{{archive.category.basename}}/{{p.year}}">See <b>{{archive.category.title}}</b> posts from {{p.year}}</a></h2>
<hr/>
% end

</div>
    <div class="col-lg-3 col-md-3 article-sidebar">
        % ssi("More At Ganriki")
    </div>
</div>

% ssi("Page Footer")

