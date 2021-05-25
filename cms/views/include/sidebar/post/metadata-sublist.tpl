% if post.id is None:
[<i>Save this post to add metadata.</i>]
% else:
% metadatas = post.get_metadata()
% if metadatas.count():
<div id="metadata-list">
% for metadata in metadatas:
<li><a class="metadata-item" data-key="{{metadata.key}}" data-value="{{metadata.value}}" data-metadata-id="{{metadata.id}}" id="kv_{{metadata.id}}" href="#"><b>{{metadata.key}}:</b> {{metadata.value}}</a>
% end
</div>
% else:
<p>[<i>No metadata for this object</i>]</p>
% end