% headers = load("Category Header Data")["headers"]
% c_header = headers.get(archive.category.title, None)

% if not c_header:
<div style="height:72px;"></div>
% end

% if c_header:

% if "title" in c_header:
<div class="jumbotron jumbotron-alt" style="padding-bottom:0px;color:white">
  <div class="fill" style="background-color:black;background-image:linear-gradient( rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.1) ),url('/img/space-background.jpg');min-height:100px;">
    <div class="container">
<h1 class="category-header-title">{{c_header["title"]}}</h1>
<div class="row spacer-bottom">
<div class="col-md-1"></div>
<div class="col-md-10">{{!c_header["text"]}}</div>
</div>
    </div>
  </div>
</div>

% else:

% book_title = archive.category.title if "display-title" not in c_header else c_header["display-title"]
<div class="jumbotron" style="padding-bottom:0px;color:white">
	<div class="fill" style="padding-bottom: 32px; background-color:black;background-image:linear-gradient( rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.1) ),url('{{c_header['background-image']}}');min-height:450px;">
      <div class="container">
        <div class="col-sm-1"></div>
      <div class="col-sm-7">
        <h1 class="category-header-title">{{book_title}}</h1>
        <h2><center><i>{{!c_header['hed']}}</i></center></h2>
        <div class=''><p>{{!c_header['dek']}}</p></div>
      </div>
        <div class="col-sm-3 jumbotron-img"><p><p/><center><img style="border: 1px solid white" src="{{c_header['cover-image']}}"></center></div>
      </div>
        <p></p>
        <div class="container jumbotron-body">
          <div class="col-xs-12">{{!c_header['blurb']}}</div>
        </div>
% if 'stub' in c_header:
          <center><button class='btn btn-primary'>{{c_header['stub']}}</button></center>
% else: 
        <p></p>
		<div class="container jumbotron-blurb"><center><h3>
          <div class="col-xs-4"><a href="https://read.amazon.com/?asin={{c_header['kindle-preview']}}"><button class='btn btn-primary'>Kindle</button></a> <a href="https://read.amazon.com/?asin={{c_header['web-preview']}}"><button class='btn btn-primary'>Web</button></a></div>
          % if 'print-edition' in c_header:
          <div class="col-xs-4"><a href="https://www.amazon.com/dp/{{c_header['print-edition']}}"><button class='btn btn-primary'>Amazon.com (Print)</button></a></div>
          % else:
          <div class="col-xs-4"><a href="#"><button class='btn btn-warning'>Print edition to come</button></a></div>
          % end
          <div class="col-xs-4"><a href="https://www.amazon.com/dp/{{c_header['kindle-edition']}}"><button class='btn btn-primary'>Amazon.com (Kindle)</button></a></div>
          </h3>
          </center>
        </div>
        <div class="container jumbotron-blurb"><center><h3>
          <div class="col-xs-4">Read the first chapters <b>FREE</b></div>
          <div class="col-xs-4">Print edition</div>
          <div class="col-xs-4">E-book edition</div>
          </h3>
          </center>
        </div>          
% end          
	<p></p>
  	</div>
</div>
% end
% end