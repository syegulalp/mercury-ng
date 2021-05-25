<form method="post">

    <div class="form-group">
        <label for="metadata_key">Key</label>
        <input type="text" class="form-control" id="metadata_key" aria-describedby="metadata_key_help"
            name="metadata_key" value="{{metadata.key}}">
        <small id="metadata_key_help" class="form-text text-muted">Key can be any text string.</small>
    </div>

    <div class="form-group">
        <label for="metadata_value">Value</label>
        <input type="text" class="form-control" id="metadata_value" aria-describedby="metadata_value_help"
            name="metadata_value" value="{{metadata.value}}">
        <small id="metadata_value_help" class="form-text text-muted">Value can be any text string.</small>
    </div>

    <div class="input-group mb-3">
        <button type="submit" name="save" value="save" class="btn btn-success">Save</button>
    </div>

    
    <div class="input-group mb-3">
        <button type="submit" name="delete" value="delete" class="btn btn-danger ">Delete</button>
    </div>

</form>