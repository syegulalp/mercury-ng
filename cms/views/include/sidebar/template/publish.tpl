% from cms.models.enums import TemplateType, TemplatePublishingMode
<input type="hidden" name="save_action" id="save_action">

% if is_new:
<div class="btn-group btn-group-wide">
    <button id="save-new-button" type="submit" class="btn btn-sm btn-primary"><span id="save-indicator"></span>Create
        new template</button>
</div>
% else:

<div class="btn-group btn-group-wide">
    <button id="save_button" data-action="save_only" type="button" class="btn btn-sm btn-success save-action"><span
            id="save-indicator"></span>Save template</button>
</div>

<div class="btn-group btn-group-wide">
    <button id="save_and_republish" data-action="save_and_republish" type="button"
        class="btn btn-sm btn-primary save-action"><span id="save_and_republish_indicator"></span>
        % if tpl.template_type in (TemplateType.INDEX, TemplateType.SSI):
        Save template and republish template files
        % else:
        Save template and republish all posts using this template
        % end
    </button>
</div>

% if tpl.template_type not in (TemplateType.SSI, TemplateType.INCLUDE, TemplateType.MEDIA):

<hr />

<div class="form-group">
    <label for="publishing_mode">Publishing mode:</label>
    <select class="form-control" id="publishing_mode" name="publishing_mode">
        % for mode in TemplatePublishingMode:
        <option value="{{mode.value}}" {{"selected" if mode==tpl.publishing_mode else ""}}>{{TemplatePublishingMode.txt[mode]}}
        </option>
        % end
    </select>
</div>

<hr/>

<div class="btn-group btn-group-wide">
    <a href="#" id="preview_button" data-action="preview" role="button" class="btn btn-sm btn-secondary">Preview
        template</a>
</div>

<div class="form-group">
    <label for="preview_id">Use this post ID to preview:</label>
    <input class="form-control" id="preview_id">
</div>

% end

<hr>

<div class="btn-group btn-group-wide">
    <a href="delete" id="delete_button" data-action="delete" role="button" class="btn btn-sm btn-danger">Delete
        template</a>
</div>

% end