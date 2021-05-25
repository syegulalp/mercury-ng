% page_title = f"Archive for tag {archive.tag.title}"
% excerpt = True
% last_year = 0
% insert("Page Head Block")
% ssi("Page Head Block SSI")
% ssi("Menu")

<div class="container clear-top">
  <div class="row">
    <div class="col-sm-9">

      <h2>Recent posts tagged <b>{{archive.tag.title}}</b></h2><hr/>

% last_year = None
      % for post in archive.posts_desc.limit(25):
% if post.date_published.year != last_year:
% last_year = post.date_published.year
<h2><a href="/tags/{{archive.tag.basename}}/{{last_year}}">{{last_year}}</a></h2><hr/>
% end
      <h4 class="archive-post-title"><a href="{{post.permalink}}">{{post.title}}</a></h4>
      <p class="archive-post-excerpt">{{!post.excerpt}}</p>
      % last_year = post.date_published.year
      % end

<hr>

<h3>
<center>
<a href="/tags/{{archive.tag.basename}}/{{last_year}}">See other <b>{{archive.tag.title}}</b> posts for <b>{{last_year}}</b></a>
</center>
</h3>

    </div>

    % insert("Sidebar")

  </div>
</div>

% ssi("Page Footer")