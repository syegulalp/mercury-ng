% article_series = post.get_metadata('Series')
% cc = load('code_module')
% cc.archive = archive
% colors, get_img = cc.tag_colors, cc.get_img

% ssi("Page Head Block SSI")
% insert("Page Head Block")
% ssi("Menu")

<!-- Page Content -->

% author_blurb = post.author.get_metadata(f'ganriki_blurb').value
% main_img, main_img_copyright, position = get_img(post)

<div id="myCarousel" class="carousel">
    <div class="carousel-inner">
        <div class="item active">
            <div class="fill" style="background-image:url('{{main_img.url}}');background-position-y:{{position}}%">
                <div class="img-caption disable-text">{{main_img_copyright}}</div>
            </div>
        </div>
    </div>
</div>

<div style="background-color: #f5f5f5">
    <div class="section section-sm container">
        <div class="col-xs-12">
            <h1 class="item-title even" data-even="3">{{post.title}}</h1>
            <h2 data-even="6" class="even-lines item-subtitle even">{{post.excerpt}}</h2>
            <p>By <a href="mailto:{{post.author.email}}"><i>{{post.author.name}}</i></a> | <a
                    href="{{post.permalink_idx}}">{{archive.datefmt(post.date_published,'%B %d, %Y')}}</a> | Share: <a
                    href="https://www.facebook.com/sharer/sharer.php?u={{post.permalink}}"><i
                        class="fa fa-facebook-square"></i></a>&nbsp;<a
                    href="https://twitter.com/home?status={{post.permalink_idx}}"><i
                        class="fa fa-twitter-square"></i></a> | <span class="badge yellow-link"><a
                        href="{{post.permalink_idx}}#disqus_thread">No comments</a></span></p>
        </div>
    </div>
</div>

<div class="section section-sm container">

    <div class="col-lg-9 col-md-9 article-body">
        % insert('Article Headers')

% if post.primary_category.title == "News":
{{!post.text}}
% else:
        <div class="lead">
        {{!post.body[0]}}
        </div>
% end

        % #ssi('Patreon Inline')

        {{!cc.replace_text(post.body[1]) if len(post.body)>1 else ""}}

        % insert('Article Footers')

        % if post.tags_public.count()>0:
        <hr style="clear:both" />
        <div class="tag-list">
            <h2>Topics:</h2>
            % for tag in post.tags_public:
            % tag_p = tag.basename.split('-',1)
            % tag_url = tag.basename
            <a href="/{{tag_p[0]}}/{{tag_p[1]}}"><span class="label label-{{!colors[tag_p[0]]}}">{{!tag.title}}</span></a>&nbsp;
            % end
        </div>
        % end

        <hr style="clear:both" />
        <h2>About the Author</h2>
        <i>{{!author_blurb}}</i>
        <hr/>

        % ssi('Disqus')

    </div>

    <div class="col-lg-3 col-md-3 article-sidebar">
        % insert("Article Series")
        % insert("Amazon Products")
        % ssi("More At Ganriki")
    </div>

</div>
% ssi("Page Footer")