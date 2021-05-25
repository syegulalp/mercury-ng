% if "search" in locals() and search is not None:
<form>
    <div class="form-group">
        <label for="search_box">Search for ... </label>
        <input type="input" name="query" class="form-control" id="search_box" aria-describedby="search_box_help" value="{{search}}">
        <small id="search_box_help" class="form-text text-muted"></small>
        % for k, v in request.query.items():
        % if k=="query":
        % continue
        % end
        <input type="hidden" name="{{k}}" value="{{v}}">
        % end
    </div>
    <button type="submit" class="btn btn-success">Submit</button>
</form>
<hr/>
% end