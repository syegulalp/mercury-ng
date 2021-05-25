% df = lambda x: archive.datefmt(x, '%B %Y')
% archive_date = df(archive.date)
% page_title = f"All posts for for {archive.category.title} in {archive_date }"
% excerpt = True
% insert("Page Head Block")
% ssi("Page Head Block SSI")
% ssi("Menu")

<div class="container clear-top">
  <div class="row">
    <div class="col-sm-9">

      <h2>All posts for <b>{{archive.category.title}}</b> in <b>{{archive_date}}</b></h2><hr>

      % for post in archive.posts_desc:
      % insert("Post Body")
      % end

<center>
% p = archive.previous
% n = archive.next
% if p:
<h3><a href="{{p.permalink_idx}}">See previous posts from {{df(p.date)}}</a>
% end
% if n:
<h3><a href="{{n.permalink_idx}}">See future posts from {{df(n.date)}}</a>
% end
</center>

    </div>
    % insert("Sidebar")
  </div>
</div>

% ssi("Page Footer")