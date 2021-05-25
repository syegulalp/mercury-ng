% if post.id is None:
[<i>Save this post to add media.</i>]
% else:
<div class="form-group">
    <label for="add_media_id">Add/remove media ID</label>
    <input type="text" class="form-control" name="add_media_id" id="add_media_id">
    <br/><button id="add_media_button" type="button" class="btn btn-sm btn-success">Add</button> <button id="remove_media_button" type="button" class="btn btn-sm btn-danger">Remove</button>
</div>
<a target="_blank" href="{{post.media_link}}">Manage this post's media</a>
<hr/>
<div id="sidebar-media-list">
% if post.media.count():
% include('include/modal/media.tpl')
% else:
[<i>No media</i>]
% end
</div>
% end