<form method="post">

    % if tab=="name":

    <div class="form-group">
        <label for="user_name">Username</label>
        <input type="text" class="form-control" id="user_name" aria-describedby="user_name_help" name="user_name"
            value="{{user.name}}">
        <small id="user_name_help" class="form-text text-muted">The name publicly associated with your posts.</small>
    </div>

    <div class="form-group">
        <label for="user_email">User email</label>
        <input type="text" class="form-control" id="user_email" aria-describedby="user_email_help" name="user_email"
            value="{{user.email}}">
        <small id="user_email_help" class="form-text text-muted">The email address associated with your user
            account.</small>
    </div>
    
    % elif tab=="password":

    <div class="form-group">
        <label for="user_password">Password</label>
        <input type="password" class="form-control" id="user_password" aria-describedby="user_password_help" name="user_password"
            value="">
        <small id="user_password_help" class="form-text text-muted">Change your password here.</small>
    </div>

    <div class="form-group">
        <label for="user_password_verify">Verify password</label>
        <input type="password" class="form-control" id="user_password_verify" aria-describedby="user_password_verify_help" name="user_password_verify"
            value="">
        <small id="user_password_verify_help" class="form-text text-muted">Type password a second time to verify.</small>
    </div>    

    % elif tab=="unlock":
        <a href="/me/unlock">Unlock posts</a>
        % editable=False
    
    % elif tab=="permissions" and admin:
        % permissions = user.permissions_detail
        % from cms.models import Blog
        % from cms.models.enums import UserPermission
        <h3>Add new permission</h3>
        <div class="form-group">
            <label for="blog_permission">Select blog</label>    
            <select class="form-control" id="blog_permission">
                <option value="0">[System]</option>
        % for blog in Blog.select().order_by(Blog.title.asc()):
                <option value="{{blog.id}}">{{blog.title}}</option>
        % end
            </select>
        </div>
        <div class="form-group">
            <label for="blog_permission">Select permission</label>    
            <select class="form-control" id="blog_permission">
        % for permission in UserPermission:
                <option value="{{permission.value}}">{{permission.name.title()}}</option>
        % end
            </select>
        </div>
        
        % if editable:
        <button type="submit" class="btn btn-success">Add permission</button>
        % end

        <hr>    
        <h3>Remove existing permissions</h3>
        % for blog, p in permissions:
        <div class="form-group form-check">
            <input type="checkbox" class="form-check-input" id="permission_{{p.id}}" name="permission" value="{{p.id}}">
            <label class="form-check-label" for="permission_{{p.id}}">{{blog.title}}: {{p.permission.name.title()}}</label>
        </div>
        
        % end
        
        % if editable:
        <button type="submit" class="btn btn-warning">Remove checked permissions</button>
        % end

    % end

    % if tab!="permissions" and editable:
    <button type="submit" class="btn btn-success">Save changes</button>
    % end

</form>