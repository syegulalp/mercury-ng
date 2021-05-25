% from cms import settings
% include('include/header.tpl')

<div class="container">
    % include('include/notice.tpl')
    % include('include/tabs.tpl')
    % if "tabs" in locals():
    <div class="container tab-contents">
    % end
    % include('include/search.tpl')
    {{!text}}
    % if "tabs" in locals():
    </div>
    % end
</div>

% include('include/footer.tpl')