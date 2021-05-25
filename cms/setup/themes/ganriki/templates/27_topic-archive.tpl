% ssi("Page Head Block SSI")
% insert("Page Head Block")
% ssi("Menu")

<div class="section section-sm container">
<div class="col-lg-9 col-md-9 article-body">

% year = 0
<h1>{{archive.category.title}} Archives</h1><hr/>

% for n in archive.posts_desc.limit(20):

% if n.date_published.year != year:
% year = n.date_published.year
<h3><a href="{{year}}">{{year}}</a></h3><hr/>
% end

% insert("Post Description")

% end
<hr/>
<h2>See more posts from <a href="/{{archive.category.basename}}/{{year}}">{{year}}</a></h2>
<hr/>

</div>
    <div class="col-lg-3 col-md-3 article-sidebar">
        % ssi("More At Ganriki")
    </div>
</div>

% ssi("Page Footer")