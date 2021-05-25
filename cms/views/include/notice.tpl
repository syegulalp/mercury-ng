% if "notice" in locals() and notice.msgs:
<div class="notifications-inner alert alert-{{notice.type}}" role="alert">
    <ul>
    % for _ in notice.msgs:
    <li>{{!_}}</li>
    % end
    </ul>
    % if notice.form:
    {{!notice.form}}
    % end
</div>
% end