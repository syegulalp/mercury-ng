% c = load("code_module")
% c.archive = archive
% get_img = c.get_img
% ssi('Page Head Block SSI')
% insert("Page Head Block")
% ssi("Menu")
% ssi("Homepage Flash Message")
% front_page_posts = archive.posts_desc.limit(9)

% insert("Homepage Carousel")

<div class="container">      

  <div class="section section-sm">
  % ssi("All Articles")
  </div>      

<div class="row">
% for post in front_page_posts[3:6]:
% media, copyright, position = get_img(post)
  <div class="col-lg-4 col-md-4 col-sm-4 portfolio-item">
    <div class="c-fix">
      <span class="img-caption-sm disable-text">{{copyright}}</span>
      <a href="{{post.permalink_idx}}"><img alt="{{media.filename}}" data-original="{{media.url}}" src="/media/gray.png" class="lazy img-responsive img-home-portfolio"/></a>
    </div>
    <span class="label label-success pull-right"></span>
    <h3 class="item-title"> <a href="{{post.permalink_idx}}">{{post.title}}</a></h3>
    <p><span class="badge yellow-link"><a href="{{post.permalink_idx}}#disqus_thread">No comments</a></span></p>
    <p class="item-dek">{{!post.excerpt}}</p>
  </div>        
% end

  </div>
</div>

<div class="section section-sm">
% ssi("All Articles")
</div>

% left = False
% for post in front_page_posts[6:9]:
% left = not left
% media, copyright, _ = get_img(post)

<div class="section {{"section-colored" if left else ""}}">
  <div class="container">
    <div class="row">

      <div class="col-lg-6 col-md-6 col-sm-6">
        <div class="c-fix">
          <span class="img-caption-sm disable-text">{{copyright}}</span>
          <a href="{{media.url}}"><img alt="{{media.filename}}" data-original="{{media.url}}" src="/media/gray.png" class="lazy img-responsive img-home-portfolio"/></a>
        </div>
      </div>

      <div class="col-lg-6 col-md-6 col-sm-6">
        <h2 class="item-title"><a href="{{post.permalink_idx}}">{{post.title}}</a></h2>
        <h4 class="item-dek">{{!post.excerpt}}</h4>
        <p><span class="badge yellow-link"><a href="{{post.permalink_idx}}#disqus_thread">No comments</a></span></p>
{{!post.body[0]}}
        <p><a href="{{post.permalink_idx}}"><i>Continue reading</i></a></p>          
      </div>

    </div>
  </div>
</div>

% end

  <div class="section section-sm">
  % ssi("All Articles")
  </div>

</div>

% ssi("Page Footer")