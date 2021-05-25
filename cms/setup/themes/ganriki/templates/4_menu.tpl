% c = load("code_module")
<nav class="navbar navbar-inverse navbar-fixed-top item-dek" role="navigation">
  <div class="container">
    <div class="navbar-header">
      <button type="button" class="navbar-toggle" data-toggle="collapse" data-target=".navbar-ex1-collapse">
        <span class="sr-only">Toggle navigation</span>
        <span class="icon-bar"></span>
        <span class="icon-bar"></span>
        <span class="icon-bar"></span>
      </button>
      <a class="navbar-brand" href="/">
        <img src="/media/ganriki-sm4.png"/><b>&nbsp;&nbsp;Ganriki:&nbsp;&nbsp;</b><small>Japan seen anew</small>
      </a>
    </div>
    <div class="collapse navbar-collapse navbar-ex1-collapse">
      <ul class="nav navbar-nav navbar-right">
        <li><a href="https://twitter.com/GanrikiDotOrg"><i class="fa fa-twitter-square"></i></a></li>
        <li>
          <form id="search-form" class="form-inline" style="" role="form" method="get" action="https://www.google.com/search">
            <div class="form-group">
              <label class="sr-only" for="google-search">Site search</label>
              <input id="google-search" type="text" name="q" maxlength="255" class="form-control input-sm" style="width:100px" placeholder="Search" data-cip-id="google-search" />
            </div>
            <button type="submit" class="btn btn-primary btn-sm">Go</button>
            <input type="hidden" name="sitesearch" value="ganriki.org"/>
          </form>
        </li>
        <li><a href="/about" title="About"><span class="glyphicon glyphicon-question-sign" aria-hidden="true"></span></a></li>
      </ul>
      <ul class="nav navbar-nav">
        <li id="new-articles" class="hidden-xs"><a id="new-articles-a" data-toggle="collapse" href="#newarticles" aria-expanded="false" aria-controls="newarticles">Latest</a></li>
        <li class="visible-xs"><a href="/article">Latest</a></li>
        <li class=""><a href="/article">Features</a></li>
        <!--
        <li class=""><a href="/news">News</a></li>
		-->
      </ul>
    </div>

    <div id="newarticles" class="container collapse">
      <div class="carousel carousel-new">
        <div id="articlelist" class="container">
% for idx, p in enumerate(archive.posts_desc.limit(3)):
% media, copyright, _ = c.get_img(p)
          <div id="article-preview-{{idx+1}}">
            <div class="col-lg-4 col-md-4 col-sm-4 portfolio-item">
              <div class="hidden-xs c-fix">
                <a href="{{p.permalink_idx}}"><img src="{{media.url}}" class="img-responsive img-home-portfolio"/></a>
              </div>
              <span class="label label-success pull-right"></span>
              <h3 class="item-title"><a href="{{p.permalink_idx}}">{{p.title}}</a></h3>
              <p class="xitem-subtitle">{{p.excerpt}}</p>
            </div>
          </div>
% end
        </div>
% next_ = archive.posts_desc.limit(4)[-1].id
        <a href="javascript:" id="nextlink" class="left carousel-control"><span class="icon-prev"></span></a>
        <a href="javascript:" id="previouslink" onclick="get_articles({{next_}},1);" class="right carousel-control"><span class="icon-next"></span></a>
        <center>
          <span class="badge yellow-link"><a href="/article">See all articles</a></span>&nbsp;&nbsp;
          <span class="badge yellow-link"><a href="/title">See all anime by title</a></span>&nbsp;&nbsp;
          <span class="badge yellow-link"><a href="javascript:{}" onclick='$("#newarticles").collapse("hide");'>Close</a></span> 
        </center>
        <br/>
      </div>
    </div>
  </div>
</nav>
