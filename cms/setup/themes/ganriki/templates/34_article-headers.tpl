% if article_series:
<div class="alert alert-info">This article is part of a series on <a href="#series"><b>{{article_series.value}}</b>.</a></div>
% end

% for n in post.tags_list:
% if n in cc.topic_headers:
{{!cc.topic_headers[n]}}
% end
% end  