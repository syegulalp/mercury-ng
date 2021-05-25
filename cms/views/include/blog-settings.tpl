% if "no_form" not in locals():
<form method="post">
% end

    % import pathlib
    % from cms.models.utils import fullpath
    % setup = "setup" in locals() 
    
    % if tab=="":

    <div class="form-group">
        <label for="blog_title">Blog title</label>
        <input type="text" class="form-control" id="blog_title" aria-describedby="blog_title_help" name="blog_title"
        value="{{blog.title}}" placeholder="Your Amazing Blog">
        <small id="blog_title_help" class="form-text text-muted">The title of your blog.</small>
    </div>

    <div class="form-group">
        <label for="blog_description">Blog description</label>
        <input type="text" class="form-control" id="blog_description" aria-describedby="blog_description_help" name="blog_description"
        value="{{blog.description}}">
        <small id="blog_description_help" class="form-text text-muted">A sentence describing your blog.</small>
    </div>

    % elif tab=="media":

    <div class="form-group">
        <label for="media_path">Blog's main media path</label>
        <input type="text" class="form-control" id="media_path" aria-describedby="media_path_help" name="media_path"
        value="{{blog.media_path}}" >
        <small id="media_path_help" class="form-text text-muted">Path in your blog's published directory where media is stored.<br><b>Do not ever delete this directory.</b><br>The current filepath resolves to:<br></small>
        % basepath = pathlib.Path(blog.base_filepath, blog.media_path)
        % try:
        % filepath = fullpath(basepath)
        % except:
        % filepath = "[Invalid path]"
        % end
        <code>{{filepath}}</code>
    </div>

    <div class="form-group">
        <label for="media_upload_path">Upload path</label>
        <input type="text" class="form-control" id="media_upload_path" aria-describedby="media_upload_path_help" name="media_upload_path"
        value="{{blog.media_upload_path}}">
        <small id="media_upload_path_help" class="form-text text-muted">Path within your media directory where new files will be uploaded.<br>
        <hr>You can use the following substitution tokens in the path:<br>
        <code>$Y</code>: Current year.<br>
        <code>$m</code>: Current month.<hr>
        The current upload path resolves to:<br></small>

        % basepath = pathlib.Path(blog.base_filepath, blog.media_path, blog.computed_media_upload_path)
        % try:
        % filepath = fullpath(basepath)
        % except:
        % filepath = "[Invalid path]"
        % end
        
        <code>{{filepath}}</code>
    </div>    

    % elif tab == "url":

    % if not setup:    
    <div class="alert alert-warning">
        Changing these settings will require your blog to be republished, and may cause any existing links to your blog to break. <b>Don't change these settings unless you are specifically altering your blog's URL or publishing location.</b>
    </div>
    % end

    <div class="form-group">
        <label for="base_url">Blog's base URL</label>
        <input type="text" class="form-control" id="base_url" aria-describedby="base_url_help" name="base_url"
        value="{{blog.base_url}}">
        <small id="base_url_help" class="form-text text-muted">Root URL of your blog. Do not include a trailing slash.</small>
    </div>

    <div class="form-group">
        <label for="base_filepath">File path for blog</label>
        <input type="text" class="form-control" id="base_filepath" aria-describedby="base_filepath_help" name="base_filepath"
        value="{{blog.base_filepath}}">
        <small id="base_filepath_help" class="form-text text-muted">Path to the directory where your blog's files will reside. Use an absolute path whenever possible.<br/>
        Changing the file path will <i>not</i> move your existing files. You must do this manually.<br>The current file path resolves to:</small>

        % basepath = pathlib.Path(blog.base_filepath)
        % try:
        % filepath = fullpath(basepath)
        % except:
        % filepath = "[Invalid path]"
        % end
        <code>{{filepath}}</code>
        % if setup:
        % if basepath.exists():
        <p><i>This directory already exists. Any files created by the blog will overwrite existing files.</i></p>
        % else:
        <p><i>This directory does not exist and will be created.</i></p>
        % end
        % end

    </div>    
    
    % end

    % if "no_button" not in locals():
    <button type="submit" class="btn btn-primary" name="submit">Save changes</button>

    % if setup:
    <button type="submit" class="btn btn-warning" name="refresh">Refresh fields to preview changes</button>
    % end

    % end
    

% if "no_form" not in locals():
</form>
% end