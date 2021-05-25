#Gzip
<ifmodule mod_deflate.c>
AddOutputFilterByType DEFLATE text/text text/html text/plain text/xml text/css application/x-javascript text/javascript+json application/javascript
</ifmodule>
#End Gzip

<filesMatch ".(css|js)$">
Header set Cache-Control "max-age=7200, must-revalidate"
</filesMatch>

AddHandler server-parsed .html

# Redirect /b /blog
Redirect /aono /writing/aono
Redirect /summerworld /writing/summerworld
Redirect /fold /writing/welcome-to-the-fold
Redirect /repairshop/non-sf-for-sf-authors /2017/05/non-sf-writing-for-sf-authors.html
Redirect /about /faq
Redirect /vajra /writing/flight-of-the-vajra/
Redirect /tokyoinferno /writing/tokyoinferno

# ^/anime/(.*?)$	/title/ # ????

# Redirect /atom.xml /rss.xml

RewriteEngine On
RewriteCond %{HTTPS} off
RewriteCond %{REQUEST_URI} !^/[0-9]+\..+\.cpaneldcv$
RewriteCond %{REQUEST_URI} !^/\.well-known/acme-challenge/[0-9a-zA-Z_-]+$
RewriteCond %{REQUEST_URI} !^/\.well-known/pki-validation/[A-F0-9]{32}\.txt(?:\ Comodo\ DCV)?$
RewriteCond %{REQUEST_URI} !^/\.well-known/cpanel-dcv/[0-9a-zA-Z_-]+$
RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
RewriteCond %{HTTP_HOST} ^genjipress\.com$ [OR]
RewriteCond %{HTTP_HOST} ^www\.genjipress\.com$
RewriteRule ^(.*)$ "https\:\/\/www\.infinimata\.com\/$1" [R=301,L]