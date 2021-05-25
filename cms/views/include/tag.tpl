<div class="alert alert-warning">
    Changing any of these fields will require your blog to be republished.
</div>

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

    <button type="submit" class="btn btn-success" name="save">Save changes</button>

</form>