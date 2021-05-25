<ul class="nav nav-tabs" id="myTab" role="tablist">
    <li class="nav-item" role="presentation">
        <a class="nav-link active" id="home-tab" data-toggle="tab" href="#home" role="tab" aria-controls="home"
            aria-selected="true">This post</a>
    </li>
    <li class="nav-item" role="presentation">
        <a class="nav-link" id="profile-tab" data-toggle="tab" href="#profile" role="tab" aria-controls="profile"
            aria-selected="false">Blog media</a>
    </li>
</ul>
<div class="tab-content" id="myTabContent">
    <div class="tab-pane fade show active" id="home" role="tabpanel" aria-labelledby="home-tab">

        <div id="post-media-list">
            % from cms.models import Media
            % for media_item in post.media.order_by(Media.id.desc()):
            <div class="media">
                <img class="mr-3 media-list-img" data-media-id="{{media_item.id}}" src="{{media_item.url}}">
                <div class="media-body">
                    <p>{{media_item.friendly_name}}</p>
                </div>
            </div>
            % end
        </div>


    </div>
    <div class="tab-pane fade" id="profile" role="tabpanel" aria-labelledby="profile-tab">

    </div>

</div>