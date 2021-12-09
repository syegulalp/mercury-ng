% if category.id:
<div class="alert alert-warning">
    Changing any of these fields will require your blog to be republished.
</div>
% end

<form method="post">

    % if category.id:
    <p><a class="btn btn-primary" role="button" href="{{category.in_posts_link}}">See all posts in this category</a></p>
    % end

    <div class="form-group">
        <label for="category_title">Category title</label>
        <input type="text" class="form-control" id="category_title" aria-describedby="category_title_help" name="category_title"
            value="{{category.title}}">
        <small id="category_title_help" class="form-text text-muted">Title for this category. Any text is acceptable as long as it isn't blank.</small>
    </div>

    <div class="form-group">
        <label for="category_description">Category description</label>
        <input type="text" class="form-control" id="category_description" aria-describedby="category_description_help" name="category_description"
            value="{{'' if category.description is None else category.description}}">
        <small id="category_description_help" class="form-text text-muted">Longer text describing this category (optional).</small>
    </div>    

    <div class="form-group">
        <label for="category_basename">Category basename</label>
        <input type="text" class="form-control" id="category_basename" aria-describedby="category_basename_help" name="category_basename"
            value="{{category.basename}}">
        <small id="category_basename_help" class="form-text text-muted">Basename created for this category. This must be unique across this blog.<br>A basename can also be a path, e.g. <code>writing/mybooks</code>, again as long as it's unique to this blog.</small>
    </div>

    <span class="float-right">
        <a href="{{category.delete_link}}">
            <button type="button" class="btn btn-danger">Delete this category</button>
        </a>
    </span>

    <button type="submit" class="btn btn-success" name="save">Save changes</button>

</form>