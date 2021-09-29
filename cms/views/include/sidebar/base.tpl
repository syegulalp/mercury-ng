<div class="accordion" id="accordionExample">
% l = locals()
% for item_id, (title, subtpl) in enumerate(sidebar_items.items()):
% body = template(f"include/sidebar/{subtpl}.tpl", **l)
% include('include/sidebar/item.tpl')
% end
</div>