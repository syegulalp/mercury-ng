% include('setup/header.tpl')

<p>Make sure the settings as listed below are OK.</p>

<hr/>

<p>Blog title: <b>{{blog.title}}</b></p>
<p>Blog description: <b>{{blog.description}}</b></p>
<p>Base URL: <b>{{blog.base_url}}</b></p>
% import pathlib
% resolved = pathlib.Path(blog.base_filepath).resolve()
<p>Base filepath: <b>{{blog.base_filepath}}</b> (Resolves to: <code>{{resolved}}</code>)</p>

<a href="/setup/4" role="button" class="btn btn-success">Continue</a>

% include('setup/footer.tpl')