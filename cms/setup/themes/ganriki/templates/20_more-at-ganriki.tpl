% get_img = load('Code')['get_img']
<div class="well">
<h4><center>More at Ganriki</center></h4>
% #ssi('See all articles') 
% for n in archive.posts_desc.limit(10):
<div class="article-sidebar">
% img, _ = get_img(n)
% if img:
<p><a href="{{n.permalink_idx}}"><img src="/media/gray.png" alt="{{img.url}}" class="img-widget lazy img-responsive" data-original="{{img.url}}" style="display: block;" /></a></p>
% end
% insert("Post Description")
</div>
% end
% #ssi('See all articles') 
</div>