% for tag in post.tags:
% btn_type = "warning" if tag.title[0] == "@" else "info"
<span class='tag-block'>
    <a target="_blank" href="{{tag.manage_link}}" data-tag="{{tag.id}}" id="tag-{{id}}" title="See details for tag '{{tag.title}}'" role="button"
        class="btn btn-{{btn_type}} btn-xs tag-title">{{tag.title}}</a><a id="tag_del_{{tag.id}}" data-tag="{{tag.id}}"
        title="Remove tag '{{tag.title}}'" role="button" class="btn btn-{{btn_type}} btn-xs tag-remove">&times;</a>
</span>
% end