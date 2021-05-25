% from cms import settings
% from cms.models.enums import editor_button_colors, PublicationStatus, editor_actions
% # from cms.models.utils import date_to_str
% from cms.routes.post import blog_sidebar as sidebar_items
% from bottle import template
%
% is_new = post.id is None
% include('include/header.tpl')
% form_action = "new-post" if post.id is None else "save"

<form id="texteditorform" method="post" action="{{form_action}}">
    <div class="container-margins">
        <div class="row">
            <div class="col texteditorcol">
                <div class="form-group">
                    <input class="form-control form-control-lg post_title enter-to-save" type="text" placeholder="Post title"
                        value="{{post.title}}" id="post_title" name="post_title">
                </div>
                <div class="form-group" id="post-text-div">
                    <textarea class="form-control" id="post_text" name="post_text">{{post.text}}</textarea>
                </div>
                <div class="form-group">
                    <label for="post_excerpt">Excerpt</label>
                    <textarea class="form-control" class="form-control" style="width:100%" id="post_excerpt"
                        name="post_excerpt">{{post.excerpt_}}</textarea>
                </div>

            </div>
            <div class="col-md-3 sidebarcol" id="sidebar-column">
                % include('include/sidebar/base.tpl')
            </div>
        </div>
    </div>
</form>

% include('include/footer.tpl')
