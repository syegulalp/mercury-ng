<div id="kv_listing">
% include('include/sidebar/post/metadata-sublist.tpl')
</div>

% if post.id is not None:
<div id="kv_group">
    <div class="form-group">
        <label for="kv_new_key_name">Key</label>
        <input class="form-control" id="kv_new_key_name" name="new_key_name" placeholder="Key name">
    </div>
    <div class="form-group">        
        <label for="kv_new_key_value">Value</label>
        <textarea class="form-control" id="kv_new_key_value" new_key_value rows="3"></textarea>
    </div>
    <input type="hidden" id="kv_id" name="kv_id">
    <button onclick="addMetadata();" id="kv_add_button" type="button" class="btn btn-sm btn-primary">Add</button>
    <button style="display:none" onclick="removeMetadata();" id="kv_delete_button" type="button" class="btn btn-sm btn-danger">Delete</button>
    <button onclick="clearMetadata();" id="kv_clear_button" type="button" class="btn btn-sm btn-secondary">Clear</button>
</div>
% end