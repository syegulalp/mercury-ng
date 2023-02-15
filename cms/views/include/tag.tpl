<form method="post">

    <p><a class="btn btn-primary" role="button" href="{{tag.in_posts_link}}">See all posts using this tag</a></p>

    <div class="form-group">
        <label for="tag_title">Tag name</label>
        <input type="text" class="form-control" id="tag_title" aria-describedby="tag_title_help" name="tag_title"
            value="{{tag.title}}">
        <small id="tag_title_help" class="form-text text-muted">Name for this tag, which should be unique across this blog.</small>
    </div>

    <div class="form-group">
        <label for="tag_basename">Tag basename</label>
        <input type="text" class="form-control" id="tag_basename" aria-describedby="tag_basename_help" name="tag_basename"
            value="{{tag.basename}}">
        <small id="tag_basename_help" class="form-text text-muted">Basename created for this tag. This must be unique across this blog.</small>
    </div>

    <div class="alert alert-warning">
    
        Changing any of these fields will require your blog to be republished. Don't make any changes on this page unless you're prepared to do that.
    </div>    

    <span class="float-right">
        <a href="{{tag.delete_link}}">
            <button type="button" class="btn btn-danger">Delete this tag</button>
        </a>
    </span>    

    <p><button type="submit" class="btn btn-primary" name="verify" value="verify">Verify short version of tag name</button></p>
    <p><button type="submit" class="btn btn-success" name="save" value="save">Save changes</button></p>
    <p>
        <a href="{{tag.merge_link}}">
            <button type="button" class="btn btn-secondary" name="merge" value="merge">Merge with another tag</button>
        </a>
    </p>

</form>