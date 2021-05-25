% prev = archive.previous_post
% next = archive.next_post
% insert("Page Head Block")
% ssi("Page Head Block SSI")
% ssi("Menu")

<div class="container clear-top">
  <div class="row">
    <div class="col-sm-9">

      % insert("Previous/Next")
      % insert("Post Body")
      % insert("Post Tags")
      % ssi("Disqus")
      % insert("Previous/Next")

    </div>

    % insert("Sidebar")

  </div>
</div>

% ssi("Page Footer")