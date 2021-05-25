% if "tabs" in locals():
<ul class="nav nav-tabs">
    % for key, tab_ in tabs.items():
    <li class="nav-item">
        <a class="nav-link{{" active" if tab==key else ""}}" href="{{tab_.link.format(tabitem=tabitem)}}">{{tab_.title}}</a>
    </li>
    % end
</ul>

% end