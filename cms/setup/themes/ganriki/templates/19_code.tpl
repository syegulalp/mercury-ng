<%
#load('Code module')
from cms import models
def get_img(post):
try:
main_img_meta = post.get_metadata('img')
main_img = models.Media.get_by_id(int(main_img_meta.value))
main_img_url = main_img.url
main_img_copyright = main_img.get_metadata('copyright').value
except Exception as e:
main_img = None
main_img_copyright = None
end
return main_img, main_img_copyright
end
%>
