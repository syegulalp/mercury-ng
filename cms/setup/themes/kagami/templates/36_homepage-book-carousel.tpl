% headers = load("Category Header Data")["headers"]
% books = ["Always Outnumbered, Never Outgunned","Flight of the Vajra","Welcome to the Fold","Summerworld"]

<div id="carousel-main" class="carousel slide" data-ride="carousel" style="top:32px;height:500px">
    <ol class="carousel-indicators">
% for idx, b in enumerate(books):
        <li data-target="#carousel-main" data-slide-to="{{idx}}" class="{{'active' if idx==0 else ''}}"></li>
% end
    </ol>

    <!-- Wrapper for slides -->
    <div class="carousel-inner" role="listbox">
% for idx, book in enumerate(books):
% book_data = headers[book]
        <div class="item {{'active' if idx==0 else ''}}">
            <div class="fill" style="background-image:url('{{book_data['background-image']}}')"></div>
            <div class="carousel-caption">
                <div class="col-xs-8">
                    <h1>{{!book}}</h1>
                    <h2>{{!book_data["hed"]}}</h2>
{{!book_data["dek"]}}
                </div>
                <div class="col-xs-4"><a href="/aono"><img style="border: 1px solid white" src="{{book_data["cover-image"]}}"></a>
                    <br><br><a href="{{book_data["permalink"]}}"><button class="btn btn-primary">Learn more</button></a>
                </div>
            </div>
        </div>
% end
    </div>

    <!-- Controls -->
    <a class="left carousel-control" href="#carousel-main" role="button" data-slide="prev">
        <span class="icon-prev"></span>
        <span class="sr-only">Previous</span>
    </a>
    <a class="right carousel-control" href="#carousel-main" role="button" data-slide="next">
        <span class="icon-next"></span>
        <span class="sr-only">Next</span>
    </a>

</div>