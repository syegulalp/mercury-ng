% if not is_new:
<p>{{!post.status_txt}}</p>
<p><b>Last saved:</b><br />
    {{post.date_last_modified_str}}</p>
<p><b>Originally created:</b><br />
    {{post.date_created_str}}</p>
<p><b>Published on:</b><br />
    {{post.date_published_str}}</p>
<p><b>Author:</b><br />
    {{post.author.name}}</p>
% #<div class="small"><a href="#">See earlier revisions</a></div>
% else:
[<i>Save this page to see its statistics.</i>]
% end
