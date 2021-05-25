% show_collapse=" show" if item_id == 0 else ""
<div class="card">
    <div class="card-header" id="heading_{{item_id}}">
        <h2 class="mb-0">
            <button class="btn btn-block text-left" type="button" data-toggle="collapse" data-target="#collapse_{{item_id}}"
            aria-expanded="true" aria-controls="collapse_{{item_id}}">
            {{title}}
        </button>            
        </h2>
    </div>

    <div id="collapse_{{item_id}}" class="collapse{{show_collapse}}" aria-labelledby="heading{{item_id}}" data-parent="#accordionExample">
        <div class="card-body">
            {{!body}}
        </div>
    </div>
</div>