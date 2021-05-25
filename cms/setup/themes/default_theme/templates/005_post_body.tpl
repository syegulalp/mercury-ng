<!-- Title -->
<h1 class="mt-4"><a href="{{post.permalink}}">{{post.title}}</a></h1>

<!-- Author -->
<p class="lead">
    by
    <a href="#">{{post.author.name}}</a>
</p>

<hr>

<!-- Date/Time -->
<p>Posted on {{post.date_published_str}}</p>

<hr>

<!-- Post Content -->
% if archive.template.template_type == archive.types.POST:
{{!post.text}}
% else:
{{!post.excerpt}}
% end

<hr>