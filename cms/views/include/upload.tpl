% import pathlib
% from cms.models.utils import fullpath
% basepath = pathlib.Path(blog.base_filepath, blog.media_path)
% upload_path = fullpath(pathlib.Path(basepath, blog.computed_media_upload_path))
% computed_custom_upload_path = fullpath(pathlib.Path(basepath,custom_upload_path ))
<h1>Advanced media upload</h1>
<hr />
<h2>Select one of the following options:</h2>

<form method="POST">
    <div class="form-check">
        <input class="form-check-input" type="radio" name="upload_option" id="default_upload_option" value="default" {{"checked" if upload_option == "default" else ""}}>
        <label class="form-check-label" for="default_upload_option">
            Upload to the default media upload path: <code>{{upload_path}}</code>
        </label>
    </div>

    <div class="form-check">
        <input class="form-check-input" type="radio" name="upload_option" id="custom_upload_option" value="custom" {{"checked" if upload_option == "custom" else ""}}>
        <label class="form-check-label" for="custom_upload_option">
            Choose a custom upload directory (set below):
        </label>
    </div>


    <hr />

    <div class="form-group">
        <label for="custom_upload_path">Custom upload path</label>
        <input type="text" class="form-control" id="custom_upload_path" aria-describedby="custom_upload_path_help"
            name="custom_upload_path" value="{{custom_upload_path}}">
        <small id="custom_upload_path_help" class="form-text text-muted">
            Supply a path, a subdirectory of your blog's media upload directory, where you want your file
            uploaded.<br>The
            current custom filepath resolves to:<br></small>

        % try:
        % filepath = fullpath(computed_custom_upload_path)
        % except:
        % filepath = "[Invalid path]"
        % end
        <code>{{filepath}}</code>
        <small>
            % if filepath.exists():
            <p><i>This directory exists. Any files uploaded that have the same name as an existing file will be automatically renamed.</i>
            </p>
            % else:
            <p><i>This directory does not exist and will be created when files are uploaded.</i></p>
            % end
        </small>

        <hr/>

        <div class="form-group">
            <label for="post_association">Post ID (optional)</label>
            <input type="text" class="form-control" name="post_association" id="post_association" aria-describedby="post_association_help" value="{{post_association}}">
            <small id="post_association_help" class="form-text text-muted">
                Supply a post ID to associate this media with.
            </small>
        </div>

        <div class="form-group">
            <label for="file_prefix">Filename prefix</label>
            <input type="text" class="form-control" name="file_prefix" id="file_prefix" aria-describedby="file_prefix_help" value="{{file_prefix}}">
            <small id="file_prefix_help" class="form-text text-muted">
                Automatically rename all uploaded files using this as a base.<br>
                If not specified, the original filenames will be used.<br>
                The file's original extension will always be reused.
            </small>
        </div>

        <button type="submit" class="btn btn-success" name="refresh">Save preferences</button>

    </div>
</form>
<hr />
<p>Once you've saved and verified your upload preferences, drag and drop one or more files here to upload.</p>
