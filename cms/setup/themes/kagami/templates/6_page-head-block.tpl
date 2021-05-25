<%

# set defaults
archive._is_post = False
page_img = f"{blog.permalink}/img/books/aono/bg.jpg"
page_title = blog.title
page_description = blog.description
page_author = blog.title

if archive.template.title == "Post":
archive._is_post = True
page_title = post.title + f" ({blog.title})"
page_description = post.excerpt
page_img = blog.permalink+"/img/"+('space-background.jpg','books/aono/bg.jpg',
   'design/wttf.jpg','summerworld-bg.jpg')[post.id % 4]
page_author = post.author.name
page_permalink = post.permalink

amazon = post.get_metadata('Amazon')
if amazon:
page_img = f"https://ws-na.amazon-adsystem.com/widgets/q?_encoding=UTF8&amp;ASIN={amazon.value}&amp;Format=_SS200_&amp;ID=AsinImage&amp;MarketPlace=US&amp;ServiceVersion=20070822&amp;WS=1&amp;tag=thegline"
end
else:
page_permalink = archive.permalink
end

%>
<!DOCTYPE html>
<html lang="en">
<head>
    <title>{{page_title}}</title>
    <link rel="canonical" href="{{page_permalink}}>
    <meta name="description" content="{{blog.description}}">
    <meta name="author" content="{{post.author if post else ''}}">
    <meta name="generator" content="{{archive.settings.PRODUCT_NAME}}" />
    <meta name="description" content="{{page_description}}" />
    % if archive._is_post:
% # depending on how twitter supports cards we may want to make this available on all pages
    <meta name="author" content="{{post.author.name}}">
    <meta name="twitter:card" content="summary">
    <meta name="twitter:site" content="@infinimata">
    <meta name="twitter:title" content="{{page_title}}">
    <meta name="twitter:description" content="{{page_description}}" />
    <meta name="twitter:image" content="{{page_img}}" />
    <meta name="twitter:image:alt" content="{{blog.title}}" />
    <meta property="og:title" content="{{page_title}}" />
    <meta property="og:type" content="article" />
    <meta property="og:image" content="{{page_img}}" />
    <meta property="og:url" content="{{page_permalink}}" />
    <script type="application/ld+json">
    {
    "@context" : "http://schema.org",
    "@type" : "Article",
    "name" : "{{post.title}}",
    "description" : "{{post.excerpt}}",
    "url" : "{{post.permalink}}",  
    "author" : {
        "@type" : "Person",
        "name" : "{{page_author}}"
    },
    "datePublished" : "{{post.date_published}}"
    }
    </script>
    % end