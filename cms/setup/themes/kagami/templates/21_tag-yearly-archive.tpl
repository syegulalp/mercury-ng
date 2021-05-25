% df = lambda x: archive.datefmt(x, '%Y')
% archive_date = df(archive.date)
% page_title = f"Archive for tag {archive.tag.title} for {archive_date}"
% insert("Page Head Block")
% ssi("Page Head Block SSI")
% ssi("Menu")

<div class="container clear-top">
  <div class="row">
    <div class="col-sm-9">

      <h2>Posts tagged <b>{{archive.tag.title}}</b> in <b>{{archive_date}}</b></h2><hr/>

      % for post in archive.posts_desc.iterator():
      <h4 class="archive-post-title"><a href="{{post.permalink}}">{{post.title}}</a></h4>
      <p class="archive-post-excerpt">{{!post.excerpt}}</p>
      % end

<center>
% p = archive.previous
% n = archive.next
% if p:
<h3><a href="{{p.permalink_idx}}">See previous posts tagged <b>{{p.tag.title}}</b> from <b>{{df(p.date)}}</b></a>
% end
% if n:
<h3><a href="{{n.permalink_idx}}">See future posts tagged <b>{{n.tag.title}}</b> from <b>{{df(n.date)}}</b></a>
% end
</center>

    </div>

    % insert("Sidebar")

  </div>
</div>

% ssi("Page Footer")