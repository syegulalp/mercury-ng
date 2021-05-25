% from cms import settings
% from cms.routes.template import template_sidebar as sidebar_items
% from cms.models.enums import TemplateType, TemplatePublishingMode
% from bottle import template
% is_new = tpl.id is None
% include('include/header.tpl')

<form id="templateeditorform" method="post" action="">
    <div class="container-margins">
        % include('include/notice.tpl')
        <div class="row">
            <div class="col texteditorcol">

                <div class="form-group">
                    <input class="form-control form-control-lg form-title-input" type="text"
                        placeholder="Template title" value="{{tpl.title}}" id="template_title" name="template_title">
                </div>
                <div class="form-group" id="template-text-div">
                    <textarea class="form-control template-editor" id="template_text"
                        name="template_text">{{tpl.text}}</textarea>
                </div>

                % if tpl.template_type not in (TemplateType.INCLUDE, TemplateType.MEDIA):

                <div class="form-group">
                    <label for="template_mapping">Template mapping</label>
                    <input class="form-control form-control-sm" type="text" placeholder="Template mapping"
                        value="{{default_mapping}}" id="template_mapping" name="template_mapping">
                </div>
                % end

            </div>
            <div class="col-md-3 sidebarcol" id="sidebar-column">
                % include('include/sidebar/base.tpl')
            </div>
        </div>
    </div>
</form>

% include('include/footer.tpl')