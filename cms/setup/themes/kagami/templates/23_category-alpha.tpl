% page_title = f"Alphabetical archive for {archive.category.title}"
% insert("Page Head Block")
% ssi("Page Head Block SSI")
% ssi("Menu")

<div class="container clear-top">
  <div class="row">
    <div class="col-sm-9">

      <h2>Alphabetical archive for <b>{{archive.category.title}}</b></h2><hr>

<ul>
      % for post in archive.posts_alpha.iterator():
<li><a href="{{post.permalink}}">{{post.title}}</a></li>
      % end

    </div>

    % insert("Sidebar")

  </div>
</div>

% ssi("Page Footer")