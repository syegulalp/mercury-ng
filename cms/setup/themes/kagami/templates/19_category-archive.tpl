% page_title = f"Archive for {archive.category.title}"
% excerpt = True
% insert("Page Head Block")
% ssi("Page Head Block SSI")
% ssi("Menu")

% insert("Category Headers")

<div class="container">
  <div class="row">
    <div class="col-sm-9">

      <h2>Recent posts in category <b>{{archive.category.title}}</b></h2><hr>

      % for post in archive.posts_desc.limit(7):
      % insert("Post Body")
      % end

<h3>
<center>
See earlier posts for <b>{{archive.category.title}}</b> from <b><a href="{{archive.category.permalink}}/{{archive.datefmt(post.date_published, '%Y/%m')}}">{{archive.datefmt(post.date_published, '%B %Y')}}</b></a>
<br><a href="/{{archive.category.basename}}/alpha">See all category posts in alphabetical order</a>
<br><a href="/{{archive.category.basename}}/chrono">See all category posts in chronological order</a>
</center>
</h3>

    </div>

    % insert("Sidebar")

  </div>
</div>

% ssi("Page Footer")