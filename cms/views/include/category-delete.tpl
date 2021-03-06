<form method="post">
    <input type="hidden" name="action_key" value="{{action_key}}">

    <div class="form-group">
        <label for="new_category">To delete a category, you must choose an existing category to move {{category.posts.count()}} posts in {{category.title}} to:</label>      
        <select class="form-control" id="new_category" name="new_category">
        % for c in categories:
              <option value="{{c.id}}" {{"selected" if c_id == c.id else ""}}>{{c.title}}</option>
        % end
        </select>
    </div>

    <p><button type="submit" class="btn btn-success" name="save2" value="save2">Move posts (batch of 25, to avoid timeout); delete category when no posts left</button></p>
    <p><button type="submit" class="btn btn-danger" name="save">Move all posts at once and delete category (long operation, may timeout)</button></p>
    
</form>