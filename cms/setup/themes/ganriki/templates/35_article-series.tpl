% from cms.models import Queue
% if article_series:
<a name="series"></a>
<div id="series-box" class="well no-ol-indent">
  <h4><center><b>{{article_series.value}}</b></center></h4>
% series_articles = archive.posts_with_metadata('Series',article_series.value).order_by(archive.post.__class__.date_published.asc())
% for idx, series_article in enumerate(series_articles):
% highlighted = "highlighted" if series_article.id == post.id else ""
<div class="article-series-item {{highlighted}}"><a href="{{series_article.permalink_idx}}">{{series_article.title}}</a></div>
% #if series_article.id==post.id and idx>0:
% #series_articles[idx-1].enqueue(neighbors=False, indices=False)
% #Queue.start(blog)
% #end
% end
</div>
% end