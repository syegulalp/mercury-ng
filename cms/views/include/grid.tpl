% from urllib.parse import urlencode
<div class="row bottom-spacer">
    <div class="col">
        {{! buttons if "buttons" in locals() else ""}}
    </div>
    <div class="col">
        <div class="btn-group btn-group-sm float-right" role="group" aria-label="">
            % qdict.update(page=1)
            <a role="button" href="?{{urlencode(qdict)}}" class="btn btn-outline-secondary">First</a>
            % qdict.update(page=prev_page)
            <a role="button" href="?{{urlencode(qdict)}}" class="btn btn-outline-secondary">Previous</a>
            <a role="button" href="#" class="btn btn-outline-secondary">{{page}} / {{start_of_page}} - {{end_of_page}} of {{total}}</a>
            % qdict.update(page=next_page)
            <a role="button" href="?{{urlencode(qdict)}}" class="btn btn-outline-secondary">Next</a>
            % qdict.update(page=last)
            <a role="button" href="?{{urlencode(qdict)}}" class="btn btn-outline-secondary">Last</a>
        </div>
    </div>
</div>

% styles = getattr(listing_model, "listing_class", None)
<table class="table table-sm table-striped table-hover">
    % if styles:
    <colgroup>
        <col>
        % for _ in styles():
            <col class="{{_}}">
        % end
    </colgroup>
    % end
    <thead>
        <tr>
            <th scope="col"><input id="box-all" type="checkbox"></th>
            % for col_label in listing_model.listing_columns(**listing_fmt):
            <th scope="col">{{!col_label}}</th>
            % end
        </tr>
    </thead>
    <tbody>
        % for item in listing:
        <tr>
            <td><input id="box={{item.id}}" type="checkbox"></td>
            % for col in item.listing(**listing_fmt):
            <td>{{!col}}</td>
            % end
        </tr>
        % end
    </tbody>

</table>