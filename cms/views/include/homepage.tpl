% from cms.models import Post, Blog
<div class="container">
    <div class="row">
        <div class="col-sm-9">
            <h3>Hello, <b>{{user.name}}</b></h3>
            </hr>
            <table class="table table-striped table-hover">
                <thead>
                    <tr>
                        <th>Title</th>
                        <th>Last edited on</th>
                        <th>Blog</th>
                    </tr>
                </thead>
                <tbody>
                    % for post in Post.select().order_by(Post.date_last_modified.desc()).limit(10):
                    <tr>
                        <td>{{!post.manage_link_html}}</td>
                        <td>{{!post.date_last_modified}}</td>
                        <td>{{!post.blog.manage_link_html}}</td>
                    </tr>
                    % end
                </tbody>
            </table>
        </div>
        <div class="col-sm-3">
            <h3>All blogs:</h3>
            <hr/>
            % for blog in Blog.select().order_by(Blog.title.asc()):
            <li>{{!blog.manage_link_html}}</li>
            % end
        </div>
    </div>