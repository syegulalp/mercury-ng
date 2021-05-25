% page_title = f"Chronological archive for {archive.category.title}"
% insert("Page Head Block")
% ssi("Page Head Block SSI")
% ssi("Menu")

<div class="container clear-top">
  <div class="row">
    <div class="col-sm-9">

      <h2>Chronological archive for <b>{{archive.category.title}}</b></h2><hr>

<ul>
      % for post in archive.posts_desc.iterator():
<li><a href="{{post.permalink}}">{{post.title}}</a> {{post.date_published}}</li>
      % end

    </div>

    % insert("Sidebar")

  </div>
</div>

% ssi("Page Footer")