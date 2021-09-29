% if is_new:
<div class="btn-group btn-group-wide">
    <button id="save-new-button" type="button" class="btn btn-sm btn-primary"><span id="save-indicator"></span>Create
        new post</button>
</div>
% else:

% from cms.models.enums import Actions, editor_actions, editor_button_colors, PublicationStatus
% actions = editor_actions[post.status]
% button_color = f"btn-{editor_button_colors[post.status]}"

<input type="hidden" name="save_action" id="save_action">

<div class="btn-group btn-group-wide">
    <button id="save-button" type="button" data-action="{{actions[0]}}"
        class="save-action btn btn-sm {{button_color}}"><span id="save-indicator"></span>{{actions[0]}}</button>
    <button type="button" class="btn btn-sm {{button_color}} dropdown-toggle dropdown-toggle-split"
        data-boundary="viewport" data-reference="parent" data-toggle="dropdown" aria-haspopup="true"
        aria-expanded="false">
        <span class="sr-only">Toggle Dropdown</span>
    </button>

    <div class="dropdown-menu dropdown-menu-right">
        % for action in actions[1:]:
        <a class="dropdown-item save-action" data-action="{{action}}" href="#">{{action}}</a>
        % end
    </div>
</div>

<div class="btn-group btn-group-wide">
    <button type="button" class="btn btn-sm btn-info save-action" data-action="Save & preview">Save & preview</button>
    <button type="button" class="btn btn-sm btn-info dropdown-toggle dropdown-toggle-split" data-boundary="viewport"
        data-reference="parent" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
        <span class="sr-only">Toggle Dropdown</span>
    </button>
    <div class="dropdown-menu dropdown-menu-right">
        <a class="dropdown-item save-action" data-action="{{Actions.Preview.PREVIEW_ONLY}}" href="#">{{Actions.Preview.PREVIEW_ONLY}}</a>
    </div>
</div>

<div class="form-group">
    <button id="close_edit" data-action="{{Actions.CLOSE}}" type="button" class="btn btn-sm btn-secondary btn-group-wide save-action">{{Actions.CLOSE}}</button>
</div>

<div class="form-group">
    <label for="publication-status">Publication status:</label>
    <h4 id="publication-status">
        <span class="badge badge-{{editor_button_colors[post.status]}}">{{PublicationStatus.txt[post.status]}}</span>
    </h4>
</div>

<div class="form-group">
    <label for="date_published">Publication date:</label>
    <input type="input" class="form-control form-control-sm enter-to-save" id="date_published" name="date_published"
        value="{{post.date_published_str}}">
</div>

% end

<div class="form-group">
    <label for="post-basename">Basename:</label>
    <div class="input-group input-group-sm mb-3">
        <input type="text" class="form-control" id="post-basename" name="post-basename" value="{{post.basename}}"
            disabled>
        <div class="input-group-append" title="Click to edit basename" id="post-basename-addon">
            <a href="#" id="post-basename-addon" class="input-group-text" >🔒</a>
        </div>
    </div>
    % if not is_new:
    <a class="small" href="#" id="regenerate_basename" style="display:none" title="Recreate basename using current post title.
Note that any existing links to this page will break.">Regenerate basename</a>
    % end
</div>

% if not is_new:

% if post.status == PublicationStatus.PUBLISHED:
% link_label = "Permalink"
% link_target = post.permalink
% else:
% link_label = "Permalink (preview only)"
% link_target = post.preview_link
% end

<div class="form-group">
    <label for="post-permalink">{{link_label}}:</label>
    <p><a class="break-anywhere" id="post-permalink" href="{{link_target}}" target="_blank">{{post.permalink}}</a>
    </p>
</div>

% end

% if not is_new:
<hr/>
<div class="form-group">
    <a href="{{post.copy_link}}" id="copy_post" type="button" class="btn btn-sm btn-group-wide btn-info">Clone this post</a>
</div>
% if post.status == PublicationStatus.DRAFT:
<div class="form-group">
    <a href="{{post.delete_link}}" id="delete_post" type="button" class="btn btn-sm btn-group-wide btn-danger">Delete this post</a>
</div>
% else:
[<i>To delete this post, unpublish or unschedule first</i>]
% end
% end