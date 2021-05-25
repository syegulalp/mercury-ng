% reformat = load("Amazon Replacement")["reformat"]
% excerpt = 'excerpt' in locals()
<h2 class="blog-post title">
% if post.primary_category != blog.default_category:
<a href="{{post.primary_category.permalink}}">{{post.primary_category.title}}</a>:
% end
<a href="{{post.permalink}}">{{post.title}}</a>
</h2>
% if excerpt:
<p class="blog-post excerpt">{{!post.excerpt}}</p>
% end

<p class="blog-post attributation">By <a class="author-name" href="{{post.author.email}}">{{post.author.name}}</a> on <span class="publication-date">{{post.date_published}}</span></p>

<hr>

% if excerpt:
% amazon = post.get_metadata("Amazon")
% if amazon:
% product = amazon.value.split(',')[0].strip()
<div class="amazon-right">
<center><small><p>Product purchases<br>support this site.</p></small>
% insert("Amazon Product")
</center></div>
% end
{{!reformat(post.body[0])}}
<p><a href="{{post.permalink}}"><span class="label label-info">Read more</span></a></p>
<hr>
% insert("Post Tags")
<hr class="entry-separator">
% else:
{{!reformat(post.body[0])}}
% if len(post.body)>1:
{{!reformat(post.body[1])}}
% end
<hr>
% end