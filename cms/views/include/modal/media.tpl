<div id="post-media-list">
    % from cms.models import Media
    % for media_item in post.media.order_by(Media.id.desc()):
    <div class="media">
        <img title="Click to insert image at cursor point" class="mr-3 media-list-img" data-media-id="{{media_item.id}}" src="{{media_item.url}}">
        <div class="media-body">
            <p><a target="_blank" href="{{media_item.manage_link}}"><b>{{media_item.id}}</b></a> / {{media_item.friendly_name}}</p>
        </div>
    </div>
    % end
</div>