% insert("Page Head Block")
% ssi("Page Head Block SSI")
% ssi("Navigation Template")

<!-- Page Content -->
<div class="container container-main">

  <div class="row">

    <!-- Post Content Column -->
    <div class="col-lg-8">

      % for post in archive.posts_desc.limit(10):
      % insert("Post Body", excerpt=True)
      % end

    </div>

    % ssi("Sidebar Template")

  </div>
  <!-- /.row -->

</div>
<!-- /.container -->

% ssi("Page Footer")