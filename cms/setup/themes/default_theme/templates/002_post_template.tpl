% insert("Page Head Block")
% ssi("Page Head Block SSI")
% ssi("Navigation Template")

<!-- Page Content -->
<div class="container container-main">

  <div class="row">

    <!-- Post Content Column -->
    <div class="col-lg-8">

      % insert("Post Body")

    </div>

    % ssi("Sidebar Template")

  </div>
  <!-- /.row -->

</div>
<!-- /.container -->

% ssi("Page Footer")