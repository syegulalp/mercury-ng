<div class="accordion" id="accordionExample">
% item_id = 0 
% l = locals()
% for title, subtpl in sidebar_items.items():
% body = template(f"include/sidebar/{subtpl}.tpl", **l)
% include('include/sidebar/item.tpl')
% item_id +=1
% end
</div>