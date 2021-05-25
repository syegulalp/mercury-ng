<!doctype html>
<html lang="en">

<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
  <meta name="description" content="">
  <title>{{page_title}}</title>
  <link rel="canonical" href="/">
  <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css"
    integrity="sha384-9aIt2nRpC12Uk9gS9baDl411NQApFmC26EwAOH8WgZl5MYYxFfc+NcPb1dKGj7Sk" crossorigin="anonymous">
  <link rel="stylesheet" href="/static/css/custom.css?{{settings.PRODUCT_VERSION}}">
  {{!headers if "headers" in locals() else ""}}
</head>

<body>
  <div id="drop-target"></div>
  <div id="drop-message"></div>
  <div id="notifications"></div>
  <div id="modal-container"></div>  
  <div class="bottom-spacer">
    <nav class="navbar sticky-top navbar-expand">
      {{!menu}}
      <div class="float-right nav-right">
        % if "blog" in locals():
        <div class="btn-group">
          <a target="_blank" href="{{blog.permalink}}">Site</a>
        </div>
        % end
        % include('include/queue-button.tpl')
        <div class="btn-group">
          <button class="btn btn-primary btn-sm dropdown-toggle" type="button" data-toggle="dropdown"
            aria-haspopup="true" aria-expanded="false">
            Me
          </button>
          <div class="dropdown-menu dropdown-menu-right">
            <a class="dropdown-item" href="/me">My settings</a>
            <a class="dropdown-item" href="/logout">Log out</a>
          </div>
        </div>
      </div>
    </nav>
  </div>