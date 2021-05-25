% if post.id is None:
[<i>Save this post to add tags.</i>]
% else:
% if "no_input" not in globals():
<div class="form-group">
    <label for="tag-input">Tag to add:</label>
    <span id="tag-progress"></span>
    <input class="form-control typeahead" id="tag-input">
</div>
% end
% t_list = [str(t.id) for t in post.tags]
<input type="hidden" id="tag_master" name="tag_master" value="{{','.join(t_list)}}">
<div id="tag-list">
    % include('include/sidebar/post/tag-sublist.tpl')
</div>
% end