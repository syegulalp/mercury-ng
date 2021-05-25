<div id="myCarousel" class="carousel slide">
  <ol class="carousel-indicators">
    <li data-target="#myCarousel" data-slide-to="0" class="active"></li>
    <li data-target="#myCarousel" data-slide-to="1"></li>
    <li data-target="#myCarousel" data-slide-to="2"></li>
  </ol>
 
  <div class="carousel-inner">
% for index, post in enumerate(front_page_posts[0:3]):
% media, copyright, position = get_img(post)

    <div class="item {{'active' if index==0 else ''}}">
      <div class="fill" style="background-image:url('{{media.url}}');background-position-y:{{position}}%">
        <div class="img-caption disable-text">{{copyright}}</div>
      </div>
      <div class="carousel-caption">
        <h1 class="item-title"><a data-even="3" class="even" href="{{post.permalink_idx}}">{{post.title}}</a></h1>
        <h4 data-even="6" class="even-lines item-subtitle even">{{post.excerpt}}</h4>
        <p><span class="badge yellow-link"><a href="{{post.permalink_idx}}#disqus_thread">No comments</a></span></p>
      </div>
    </div>
% end
  </div>
  <a class="left carousel-control" href="#myCarousel" data-slide="prev">
    <span class="icon-prev"></span>
  </a>
  <a class="right carousel-control" href="#myCarousel" data-slide="next">
    <span class="icon-next"></span>
  </a>  
</div>