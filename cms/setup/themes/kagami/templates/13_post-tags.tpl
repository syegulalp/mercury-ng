% if post.tags.count():
<div class="blog-post tag-list">Tags:
% for tag in post.tags:
<a href="/tags/{{tag.basename}}"><span class="label label-primary">{{tag.title}}</span></a>
% end
</div><hr/>
% end