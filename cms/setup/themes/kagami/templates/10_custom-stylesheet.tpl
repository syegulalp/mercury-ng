/* for BS 3.3.7 */

@font-face {
    font-family: 'bebas_neueregular';
    src: url('/img/fonts/bebasneue-regular-webfont.woff2') format('woff2'), url('/img/fonts/bebasneue-regular-webfont.woff') format('woff');
}

/* Responsive Styles */

@media (max-width: 768px) {
    .jumbotron-img {
        text-align: center
    }
    .carousel-caption h1 {
        font-size: 36px;
    }
    h1.category-header-title {
        padding-top: 16px;
    }
}

@media (max-width: 650px) {
    .carousel img {
        zoom: 75%;
    }
    .carousel {
        zoom: 66%;
    }
    .carousel-caption {
        xpadding-top: 72px;
        right: 10%;
        left: 10%;
    }
    h1.category-header-title {
        line-height: 32px;
    }
}

@media (min-width: 769px) {
    h1.category-header-title {
        line-height: 56px;
    }
}

.link-next-post {
    text-align: right;
}

.mt-image-center {
    width: 75%;
    margin: 1.5em auto 1.5em auto;
}

.mt-image-center img {
    width: 100%;
}

.blog-post.title {
    font-weight: 700;
    margin-top: 0;
}

.blog-post.excerpt {
    font-style: italic;
    margin: 0 1em 1em 1em;
}

.blog-post.attributation {
    font-size: 1.25rem;
}

.blog-post.attributation .author-name {
    font-weight: bold;
}

.blog-post.attributation .publication-date {
    font-weight: bold;
}

.clear-top {
    margin-top: 72px;
}

html {
    min-height: 100%;
}

body {
    background-color: #fcf6ef;
    font-size: 1.5rem;
}

.footer {
    width: 100%;
    height: 64px;
    background-color: #f5f5f5;
    padding-top: 24px;
    margin-top: 24px;
}

code {
    font-size: 90%;
}

.img-thumbnail {
    width: 50%;
}

blockquote {
    font-size: inherit;
    line-height: 1.3em;
}

.article-nav {
    font-size: 90%;
    margin-top: 15px;
    margin-bottom: -15px;
}

.featurette-divider {
    clear: all
}

.fill {
    width: 100%;
    height: 100%;
    background-position: center;
    background-size: cover;
}

.item, .active, .carousel-inner {
    height: 100%;
}

.carousel-caption {
    top: 33px;
    max-width: 800px;
    margin: auto;
}

.carousel-caption h1 {
    margin-top: 8px;
    font-family: 'bebas_neueregular';
    font-size: 56px;
    line-height: 50px;
}

.entry-separator {
    border-top: 4px solid #eeeeee;
}

.screenshot {
    text-align: center;
    font-weight: bold;
    font-size: 0.85em;
    margin-bottom: 1em;
}

.screenshot img {
    width: 48%;
    margin: .5em .2% .5em .2%;
}

.screenshot-double img {
    width: 48%;
}

.jumbotron-blurb p {
    font-size: 1em;
}

h4.widget-header {
    font-weight: bold;
}

.widget {
    font-size: small;
    line-height: 1.25;
}

.widget input {
    width: 100%;
}

.widget ul {
    padding: 0 0 0 2em;
}

.amazon-img {
    min-width: 100px;
}

.amazon-img a img {
    width: auto;
}

.amazon-right {
    float: right;
    margin: 0 0 1em 1em;
}

.amazon-left {
    float: left;
    margin: 0 1em 1em 0;
}

.pclear-left {
    clear: right;
}

.jumbotron-body p {
    font-size: 16px;
}

.jumbotron-alt p {
    font-size: 15px;
}

.jumbotron-body a {
    color: yellow;
}

.book-lineup {
    width: 100%;
    text-align: center;
}

.book-lineup img {
    width: 15%;
}

img.img-featured {
    width: auto;
    max-height: 50vh;
    margin: 1.25em auto 1.25em auto;
}

.bright-link a {
    color: white;
}

h1.category-header-title {
    font-family: 'bebas_neueregular';
    text-align: center;
}

tr:nth-child(even) {
    background: #EEE
}

tr:nth-child(odd) {
    background: #FFF
}

img.pull-right {
    margin-left: 8px;
}

#navbar .title-link {
    font-family: 'bebas_neueregular';
}

.purchase-link {
    font-size: 1.2rem;
    line-height: 1.4rem;
    margin-top: 8px;
}

.jumbotron a {
    color: yellow;
}

.spacer-bottom {
    margin-bottom: 24px;
}

.archive-post-excerpt {
    font-size: 1.4rem;
    font-style: italic;
}