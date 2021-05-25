% c = load('code_module')
% main_img, main_img_copyright, _ = c.get_img(post)
% prev = getattr(archive.previous_post,'id',0)
% next = getattr(archive.next_post,'id',0)
<div 
data-previous="{{prev}}"
data-next="{{next}}"
data-prev-abs="{{prev}}"
data-next-abs="{{next}}"
class="col-lg-4 col-md-4 col-sm-4 portfolio-item">
  <div class="hidden-xs c-fix">
    % #<span class="img-caption-sm disable-text">{{main_img_copyright }}</span>
    <a href="{{post.permalink_idx}}">
  <img alt="{{main_img.url}}" src="{{main_img.url}}" class="img-responsive img-home-portfolio"></a>
  </div>
  <span class="label label-success pull-right"></span>
  <h3 class="item-title"><a href="{{post.permalink_idx}}">{{post.title}}</a></h3>
  <p class="item-dek">{{!post.excerpt}}</p>
</div>