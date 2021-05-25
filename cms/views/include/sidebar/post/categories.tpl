% from cms.models import Category
% if post.id is None:
% post_categories = []
% primary_cat_id = None
% else:
% post_categories = [x[0] for x in post.categories.select(Category.id).tuples()]
% primary_cat_id = post.primary_category.id
% end
<div id="category-list">
    <div class="form-group">
        <label for="primary-category">Primary category</label>
        <select class="form-control" id="primary-category" name="primary_category">
            % for category in blog.categories.order_by(Category.default.desc(),Category.title.asc()):
            <option value="{{category.id}}" {{"selected" if category.id==primary_cat_id else ""}}>{{category.title}}
            </option>
            % end
        </select>
    </div>
    <label>Other categories:</label>
    % for category in blog.categories.where(Category.id != primary_cat_id).order_by(Category.default.desc(), Category.title.asc()):
    <div class="form-check">
        % checked = "checked" if category.id in post_categories else ""
        <input class="form-check-input" {{checked}} name="subcategory" type="checkbox" value="{{category.id}}" id="subcategory-{{category.id}}">
        <label class="form-check-label" for="subcategory-{{category.id}}">{{category.title}}</label>
    </div>
    % end
</div>