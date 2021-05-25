% try:
% products = post.get_metadata('Amazon').value.split(',')
% except:
% products = None
% end

% if products is not None:
  <div class="well">
    <center>
      <h4>Related Products</h4>
    <small><p>Product purchases<br/>support their creators<br/>and this site.</p></small>
% for product in products:
% product = product.strip()
% if product:
      <span class="amazon-product"><a href="http://www.amazon.com/dp/{{product}}/?tag=thegline"><img class="img img-responsive" alt="Purchase at Amazon" title="Purchase at Amazon" border="0" src="//ws-na.amazon-adsystem.com/widgets/q?_encoding=UTF8&MarketPlace=US&ASIN={{product}}&ServiceVersion=20070822&ID=AsinImage&WS=1&Format=_SL250_&tag=thegline"/></a><img src="//ir-na.amazon-adsystem.com/e/ir?t=thegline&l=am2&o=1&a={{product}}" width="1" height="1" border="0" alt="" style="border:none !important; margin:0px !important;"/></span>
% end
% end
</center></div>
% end