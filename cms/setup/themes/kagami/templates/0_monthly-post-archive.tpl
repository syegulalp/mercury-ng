% date_range = archive.datefmt(archive.date, '%B %Y')
% page_title = f"All posts for {date_range}"
% excerpt = True
% insert("Page Head Block")
% ssi("Page Head Block SSI")
% ssi("Menu")

<div class="container clear-top">
  <div class="row">
    <div class="col-sm-9">

      <h2>All posts for <b>{{date_range}}</b></h2><hr>

      % for post in archive.posts_desc:
      % insert("Post Body")
      % end

    </div>

    % insert("Sidebar")

  </div>
</div>

% ssi("Page Footer")