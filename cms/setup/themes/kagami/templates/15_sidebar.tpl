<div class="col-sm-3">
% if archive._is_post:
% amazon = post.get_metadata('Amazon')
% if amazon:
% products = amazon.value.rstrip(',').split(',')
<div class="well well-small widget">
<center><small><p>Product purchases<br>support this site.</p></small>
% for product in products:
% product = product.strip()
% insert("Amazon Product")
% end
</center>
</div>
% end
% end

<div class="well well-small widget">
% if archive._is_post:
  <h4 class="widget-header">About This Page</h4>

% category_list = [f'<a href="/{category.basename}">{category.title}</a>' for category in post.categories]
% cat_indicator = "categories" if len(category_list)>1 else "category"
<p>This page contains a single post by <a href="mailto:{{post.author.email}}">{{post.author.name}}</a>, in the {{cat_indicator}} {{!', '.join(category_list)}}, published on <i>{{post.date_published}}.</i></p>
<p><a href="/{{post.date_published.year}}/{{post.date_published.month}}">See all entries for {{archive.datefmt(post.date_published, '%B %Y')}}.</a></p>
<p><a href="/{{post.date_published.year}}">See all entries in {{archive.datefmt(post.date_published, '%Y')}}.</a></p>

% elif archive.template.title in ("Category Archive", "Category Monthly Archive","Category Alpha","Category Chrono"):
  <h4 class="widget-header">About This Page</h4>
<p>This page contains an archive of posts in the category <b>{{archive.category.title}}</b>.</p>
<p><a href="/{{archive.category.basename}}/alpha">See all category posts in alphabetical order.</a></p>
<p><a href="/{{archive.category.basename}}/chrono">See all category posts in chronological order.</a></p>
% else:
  <h4 class="widget-header">{{blog.title}}</h4>
<p><small>{{blog.description}}</small></p>
% end
<p>Find recent content on the <a href="/">main index</a> or look in the <a href="/b">archives</a> to find all content.</p>
</div>

% ssi("Sidebar SSI")

</div>
