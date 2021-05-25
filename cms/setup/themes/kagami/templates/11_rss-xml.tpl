<%
posts = archive.posts_desc.limit(7)
tf = "%a, %d %b %Y %H:%M:%S -0000"
import datetime
dt = datetime.datetime.utcnow()
date_now = dt.strftime(tf)
try:
 	pub_date = posts[0].date_published.strftime(tf)
except:
 	pub_date = date_now
end
%>
<rss version="2.0">
   <channel>
      <title>{{blog.title}}</title>
      <link>{{blog.permalink}}</link>
      <description>{{blog.description}}</description>
      <language>en-us</language>
      <pubDate>{{pub_date}}</pubDate>
      <lastBuildDate>{{pub_date}}</lastBuildDate>
      <generator>{{archive.settings.PRODUCT_NAME}}</generator>
      <ttl>60</ttl>
      % for p in posts:
      <item>
         <guid>{{p.permalink}}/?{{p.id}}</guid>
         <title>{{p.title}}</title>
         <link>{{p.permalink}}</link>
         <description>{{p.excerpt}}</description>
         <author>{{p.author.email}} ({{p.author.name}})</author>
         <pubDate>{{p.date_published.strftime(tf)}}</pubDate>
      </item>
      % end
   </channel>
</rss>
