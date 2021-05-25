<%

nav_links = [
["Home","/"],
["About","/about"],
["Contact","/contact"]
]

%>

<!-- Navigation -->
<nav class="navbar navbar-expand-lg navbar-dark bg-dark fixed-top">
  <div class="container">
    <a class="navbar-brand" href="#">{{blog.title}}</a>
    <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarResponsive"
      aria-controls="navbarResponsive" aria-expanded="false" aria-label="Toggle navigation">
      <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse" id="navbarResponsive">
      <ul class="navbar-nav ml-auto">
        % for link in nav_links:
        <li class="nav-item">
          <a class="nav-link" href="{{link[1]}}">{{link[0]}}
          </a>
        </li>
        % end
      </ul>
    </div>
  </div>
</nav>