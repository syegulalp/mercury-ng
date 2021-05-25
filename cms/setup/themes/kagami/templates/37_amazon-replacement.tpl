<%
import regex as re

amazon_re = re.compile('(<p>|<h\d>)(.*?)((<a [^>]*?href=")(left.|right.)*?amazon.com:([^"]*?)">)(.*?)</a>(.*?</p>)')

affiliate = "Affiliate link. Product purchases support this site."

lr = (' amazon-left',' amazon-right')

def reformat(text):
    direction = False
    for match in amazon_re.finditer(text):
        direction = not direction
        product = match[6]
        link = f"https://www.amazon.com/gp/product/{product}/ref=as_li_ss_il?ie=UTF8&amp;camp=1789&amp;creative=390957&amp;creativeASIN={product}&amp;linkCode=as2&amp;tag=thegline"
        #position = "" if not match[5] else f" amazon-{match[5][:-1]}"
position = "" if not match[5] else lr[direction]
        if not position:
            replacement = f'''{match[1]}{match[2]}<a title="{affiliate}" href="{link}" target="_blank">{match[7]}</a>{match[8]}'''
        else:
            replacement = f'''<div class="amazon-img{position}" style="text-align:center"><a href="{link}" target="_blank"><img alt="Purchase on Amazon" title="Purchase on Amazon" src="https://ws-na.amazon-adsystem.com/widgets/q?_encoding=UTF8&amp;ASIN={product}&amp;ID=AsinImage&amp;MarketPlace=US&amp;ServiceVersion=20070822&amp;WS=1&amp;tag=thegline&amp;" class=""></a><div class="purchase-link">Product purchases support this site.</div></div>{match[1]}{match[2]}<a title="{affiliate}" href="{link}">{match[7]}</a>{match[8]}'''
        end
        text = text.replace(match[0], replacement,1)
    end
    return text
end
%>