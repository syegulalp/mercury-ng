% filename_body, filename_ext = media.filename_parts
<div class="row">
    <div class="col-6">
        <img class="img-fluid media-edit-image" src="{{media.url}}">
    </div>
    <div class="col-6">
        <h2>{{media.filepath}}</h2>
        <hr />
        <form method="POST">

            <div id="media-filename-outer-div" class="form-group">
                <label for="media-filename">Name (edit to rename file):</label>
                <div id="media-filename-div" class="input-group mb-3">
                    <input class="form-control form-control-lg" placeholder="{{filename_body}}" id="media-filename"
                        name="media_filename" value="{{filename_body}}">
                    <div class="input-group-append">
                        <span class="input-group-text" id="basic-addon2">.{{filename_ext}}</span>
                    </div>
                </div>
            </div>

            <div id="media-description-div" class="form-group">
                <label for="friendly_name">Detailed description:</label>
                <textarea class="form-control" id="friendly_name"
                    name="friendly_name">{{!media.friendly_name}}</textarea>
            </div>

            <div id="media-path-div" class="form-group">
                <label for="media-path">Full path:</label>
                <input class="form-control form-control" id="media-path"
                    value="{{media.full_filepath}}" disabled>
            </div>            

            <div id="media-size-div" class="form-group">
                <label for="media-size">Size (in bytes):</label>
                <input class="form-control form-control" id="media-size"
                % filesize = f"{media.filesize:,}"
                    value="{{filesize}}" disabled>
            </div>

            <div id="media-datetime-div" class="form-group">
                <label for="media-datetime">Date uploaded:</label>
                <input class="form-control form-control" id="media-datetime"
                    value="{{media.date_created_str}}" disabled>
            </div>

            <div class="form-group">
                <button type="submit" name="save" value="save" class="btn btn-sm btn-success">Save changes</button>
            </div>

            <div class="form-group form-check">
                <input type="checkbox" id="no_rename" name="no_rename" value="no_rename" class="form-check-input">
                <label class="form-check-label" for="no_rename">Don't rename references to this image</label>
                <small id="rename_help" class="form-text text-muted">References will never be renamed in posts currently
                    open for editing.</small>
            </div>

            <hr />

            % post = media
            % include('include/sidebar/post/metadata.tpl')

        </form>
    </div>
</div>
<hr>
<span class="float-right">
    <a href="{{media.delete_link}}">
        <button type="button" class="btn btn-sm btn-danger">Delete this image</button>
    </a>
</span>

<a href="{{media.used_in_link}}">
    <button type="button" class="btn btn-sm btn-secondary">See all posts using this media</button>
</a>