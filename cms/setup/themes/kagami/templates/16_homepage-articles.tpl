<%

main_blog_posts = archive.posts_desc.limit(1).get()
writing_posts = archive.posts_in_categories(("Infinimata Press: Projects",)).get()
review_posts = archive.posts_in_categories(("Music","Movies","Books")).get()

cat_titles = ("The Blog","The Writing","The Reviews")
categories = (main_blog_posts, writing_posts, review_posts)
%>

    <div class="row">
% for cat_title, cat_post in zip(cat_titles, categories):

        <div class="col-sm-4">
            <a href="{{cat_post.primary_category.permalink}}">
                <h2>{{cat_title}}:</h2>
            </a>
            <h3><a href="{{cat_post.permalink}}">{{cat_post.title}}</a></h3>
            <p>{{!cat_post.excerpt}}</p>
            <p><a href="{{cat_post.permalink}}"><button class="btn btn-primary">Read more »</button></a></p>
        </div>

% end

    </div>