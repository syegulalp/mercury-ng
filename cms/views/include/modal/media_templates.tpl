<div id="post-media-list">
    <div class="media">
        <img class="mr-3 media-list-img" data-media-id="{{media.id}}" src="{{media.url}}">
        <div class="media-body">
            <p>{{media.friendly_name}}</p>
        </div>
    </div>
<hr/>
<p>Choose a template type:</p>
<ul>
% for template in blog.media_templates:
<li><a href="#" class="media-list-template" data-media-id="{{media.id}}" data-template-id="{{template.id}}">{{template.title}}</a></li>
% end
</ul>