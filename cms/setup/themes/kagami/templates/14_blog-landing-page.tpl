% excerpt=True
% insert("Page Head Block")
% ssi("Page Head Block SSI")
% ssi("Menu")

<div class="container clear-top">
  <div class="row">
    <div class="col-sm-9">

      % for post in archive.posts_desc.limit(10):
      % insert("Post Body")
      % end

<hr>
<h2>See earlier posts from <b><a href="/{{archive.datefmt(post.date_published, '%Y/%m')}}">{{archive.datefmt(post.date_published, '%B %Y')}}</b></a></h2>

    </div>

    % insert("Sidebar")

  </div>
</div>

% ssi("Page Footer")