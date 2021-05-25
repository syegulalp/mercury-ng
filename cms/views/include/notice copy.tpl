% if "notice" in locals() and notice is not None:
% style = notice[0]
% text = notice[1]
<div class="alert alert-{{style}}" role="alert">
    {{!text}}
</div>
% end