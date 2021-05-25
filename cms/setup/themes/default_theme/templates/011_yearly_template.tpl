% excerpt = True
% insert("Page Head Block")
% ssi("Page Head Block SSI")
% ssi("Navigation Template")

<!-- Page Content -->
<div class="container container-main">

  <div class="row">

    <!-- Post Content Column -->
    <div class="col-lg-8">

      <h2>Archive for {{archive.datefmt(archive.date, '%Y')}}</h2>

      % for post in archive.posts_desc:
      <h4>{{post.title}}</h4>
      <p>{{post.excerpt}}</p>
      % end

    </div>

    % ssi("Sidebar Template")

  </div>
  <!-- /.row -->

</div>
<!-- /.container -->

% ssi("Page Footer")