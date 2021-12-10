<form method="post">
    
    <div class="form-group">
        <label for="tag_title">Merge tag <b>{{old_tag.title}}</b> (#{{old_tag.id}}) with this tag:</label>
        <input type="text" class="form-control" id="tag_title" aria-describedby="tag_title_help" name="tag_title"
            value="{{new_tag.title}}">
        <small id="tag_title_help" class="form-text text-muted"></small>
    </div>

    <div class="alert alert-warning">
        Changing any of these fields will require your blog to be republished. Don't make any changes on this page unless you're prepared to do that.
    </div>    

    <p><button type="submit" class="btn btn-primary" name="verify" value="verify">Verify changes</button></p>
    <p><button type="submit" class="btn btn-success" name="save" value="save">Merge tag (25 posts at a time)</button></p>

</form>