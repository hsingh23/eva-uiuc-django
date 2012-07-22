//check for enter in input field
$(document).ready(function() {
    $(".fancybox").fancybox({
        openEffect : 'none',
        closeEffect : 'none',
        helpers : {
            title : {
                type : 'outside'
            }
        }
    });
    $(".various").fancybox({
        // maxWidth : 800,
        // maxHeight    : 600,
        fitToView   : false,
        width       : '90%',
        height      : '90%',
        autoSize    : false,
        closeClick  : false,
        openEffect  : 'none',
        closeEffect : 'none'
    });
    $('#in-field').bind('keypress', function(e) {
        var code = e.keyCode || e.which;
        if(code === 13) {
            load_results($('#in-field').val());
            disable_input();
            return false;
        }
    });
    load_initial_data();

});

function disable_input(){
    $('#in-field').attr("disabled", "disabled");
    setTimeout('$("#in-field").removeAttr("disabled");',2000);
}

function my_search(search_term){
    if (search_term[0] === '#'){
        $('#in-field').val(search_term.replace('#',$.initial_search_term));
    }
    else{
        $('#in-field').val(search_term)
    }
    load_results($('#in-field').val());
    return false;
}

function getQueryVariable(variable)
{
    var query = window.location.search.substring(1);
    var vars = query.split("&");
    for (var i=0;i<vars.length;i++){
        var pair = vars[i].split("=");
        if (pair[0] == variable){
            return pair[1];
        }
    }
    return "Computer Science"; //not found
}

function load_initial_data(){
    var initial = getQueryVariable("q");
    $.getJSON('get-initial/?search='+initial+'&callback=?', function(data) {
        console.log(data);
        parse(data);
    });
}

function parse(data){
    if (data.initial_search_term){
        load_results(data.initial_search_term);
        $.initial_search_term = data.initial_search_term;
        $('#in-field').val(data.initial_search_term);
    }

    var suggested_search = [];
    $.each(data.suggested_search, function(key, val) {
        suggested_search.push('<ul><a href="#" class="toggle" onclick="my_search(\''+val+'\');">'+val+'</a></ul>');
    });

    $('#suggested_search').append(suggested_search.join('\n'));
    var related_search = [];
    $.each(data.related_search, function(key, val) {
        related_search.push('<ul><a href="#" class="toggle" onclick="my_search(\''+val+'\');">'+val+'</a></ul>');
    });
    $('#related_search').append(related_search.join('\n'));

    var initial_swf = [];
    $.each(data.initial_swf, function(key, val) {
        initial_swf.push('<ul><a class="various" href="'+val+'">'+key+'</a></ul>');
    });
    $('#sidebar-swf').append(initial_swf.join('\n'));

    var videos = [];
    $.each(data.initial_youtube_id, function(key, val) {
        videos.push('<div class="item"><iframe class="youtube-player" type="text/html" width="100%" height="500px" src="http://www.youtube.com/embed/'+val+'?wmode=transparent" frameborder="0"></iframe></div>');
    });
    $('#video_flow_items').prepend(videos.join('\n'));

    var items = [];
    $.each(data.initial_images, function(key, val) {
        //change index to key
        if (key%4 === 0) {
            if (key === 0) {
                items.push('<div class="item"><ul class="thumbnails"><li class="span3"><div class="thumbnail"><a class="fancybox" href="'+val+'"><img src="'+val+'" alt="" height="125px" width="100%"></a></div></li>');
            }
            else {
                items.push('<div class="item"><ul class="thumbnails"><li class="span3"><div class="thumbnail"><a class="fancybox" href="'+val+'"><img src="'+val+'" alt="" height="125px" width="100%"></a></div></li>');
            }
        }
        else if (key%4 !== 3){
            items.push('<li class="span3"><div class="thumbnail"><a class="fancybox" href="'+val+'"><img src="'+val+'" alt="" height="125px" width="100%"></a></div></li>');
        }
        else {
            items.push('<li class="span3"><div class="thumbnail"><a class="fancybox" href="'+val+'"><img src="'+val+'" alt="" height="125px" width="100%"></a></div></li></ul></div>');
        }
    });
    $('#picture_flow_items').prepend(items.join('\n'));
}

function load_from_api(search){
    $.getJSON('/api/'+search+'?callback=?', function(data) {
        var pdf = [];
        var sidebar_pdf = [];
        $.each(data.pdf, function(key, val) {
            if (key <= 2) {
                sidebar_pdf.push('<ul><a class="various fancybox.iframe" href="https://viewer.zoho.com/api/urlview.do?embed=true&url='+val[1]+'">'+val[0]+'</a></ul>');
            }
            pdf.push('<ul><a class="various fancybox.iframe" href="https://viewer.zoho.com/api/urlview.do?embed=true&url='+val[1]+'"><font size="5">'+(key+1)+') '+val[0]+'</font></a></ul>');
        });
        $('#sidebar-pdf').append(sidebar_pdf.join('\n'));
        $('#pdf').append(pdf.join('\n'));
        var items = [];
        //console.log(data.facts)
        $.each(data.img, function(index, val) {
            if (index <= 15) {
                if (index%4 === 0) {
                    if (index === 0) {
                        items.push('<div class="item"><ul class="thumbnails"><li class="span3"><div class="thumbnail"><a class="fancybox" href="'+val[0]+'"><img src="'+val[1]+'" alt="" height="125px" width="100%"></a></div></li>');
                    }
                    else {
                        items.push('<div class="item"><ul class="thumbnails"><li class="span3"><div class="thumbnail"><a class="fancybox" href="'+val[0]+'"><img src="'+val[1]+'" alt="" height="125px" width="100%"></a></div></li>');
                    }
                }
                else if (index%4 !== 3){
                    items.push('<li class="span3"><div class="thumbnail"><a class="fancybox" href="'+val[0]+'"><img src="'+val[1]+'" alt="" height="125px" width="100%"></a></div></li>');
                }
                else {
                    items.push('<li class="span3"><div class="thumbnail"><a class="fancybox" href="'+val[0]+'"><img src="'+val[1]+'" alt="" height="125px" width="100%"></a></div></li></ul></div>');
                }
            }
        });
        $('#picture_flow_items').append(items.join('\n'));
    });
}

//get them results
function load_results(orig_search){
    var HelpSpace = HelpSpace || {};
    wiki_search = orig_search.replace(/ /g,"_");
    search = encodeURIComponent(orig_search);
    var pic_flow = $('#picture_flow_items');
    var vid_flow = $('#video_flow_items');
    var sidebar_pdf = $('#sidebar-pdf');
    var sidebar_swf = $('#sidebar-swf');
    vid_flow.empty();
    pic_flow.empty();
    sidebar_pdf.empty();
    sidebar_swf.empty();

    var wikipedia_url = 'http://www.wikipedia.org/w/api.php?action=query&prop=extracts&format=json&exintro=&explaintext=&exsectionformat=plain&titles='+wiki_search+'&redirects&callback=?';
    $.getJSON(wikipedia_url, function(data) {
        var heading;
        var extract;
        // if (data.query.pages["-1"])
        $.each(data.query.pages, function(index, val) {
            heading = '<strong><a class="various fancybox.iframe" href="http://en.wikipedia.org/wiki/'+val.title+'?printable=yes">Wikipedia: '+val.title+'</a></strong>';
            if (val.missing === "") {
                extract = 'Not found on Wikipedia, click on the title above for redirection';
            }
            else {
                extract = '<p>'+val.extract+'</p>';
            }
            // console.log(heading, extract);
        });
        $('.wiki_title').empty();
        $('.wiki_extract').empty();
        $('.wiki_title').append(heading);
        $('.wiki_extract').append(extract);
    });

    //#######warning: is depricating and may stop working at any time
    var google_url = 'https://ajax.googleapis.com/ajax/services/search/images?v=1.0&q='+search+'&safe=active&rsz=8&callback=?';
    $.getJSON(google_url, function(data) {

        var items = [];
        $.each(data.responseData.results, function(index, val) {
            if (index%4 === 0) {
                if (index === 0) {
                    items.push('<div class="item active"><ul class="thumbnails"><li class="span3"><div class="thumbnail"><a class="fancybox" href="'+val.url+'" title="'+val.titleNoFormatting+'"><img src="'+val.tbUrl+'" alt="" height="125px" width="100%"></a></div></li>');
                }
                else {
                    items.push('<div class="item"><ul class="thumbnails"><li class="span3"><div class="thumbnail"><a class="fancybox" href="'+val.url+'" title="'+val.titleNoFormatting+'"><img src="'+val.tbUrl+'" alt="" height="125px" width="100%"></a></div></li>');
                }
            }
            else if (index%4 !== 3){
                items.push('<li class="span3"><div class="thumbnail"><a class="fancybox" href="'+val.url+'" title="'+val.titleNoFormatting+'"><img src="'+val.tbUrl+'" alt="" height="125px" width="100%"></a></div></li>');
            }
            else {
                items.push('<li class="span3"><div class="thumbnail"><a class="fancybox" href="'+val.url+'" title="'+val.titleNoFormatting+'"><img src="'+val.tbUrl+'" alt="" height="125px" width="100%"></a></div></li></ul></div>');
            }
        });
        pic_flow.append(items.join('\n'));
    });

    // Get images from bing
    // #######warning: is depricated and will stop working August 1 2012
    // #######warning: CAN RETURN DANGEROUS CONTENT: Removed for now

    // var bing_url = 'http://api.bing.net/json.aspx?AppId=9B2B80CDB8B7ED402F4D7D79B8243F25F8A95B2E&Query='+search+'&Sources=Image&Version=2.0&Market=en-us&Adult=Moderate&Image.Count=15&Image.Offset=0&JsonType=callback&JsonCallback=?'
    // $.getJSON(bing_url, function(data) {
    //  var items = [];

    //  $.each(data.responseData.results, function(index, val) {
    //      if (index%4 === 0) {
    //          if (index === 0) {
    //              items.push('<div class="item active"><ul class="thumbnails"><li class="span3"><div class="thumbnail"><a class="fancybox" href="'+val.MediaUrl+'" title="'+val.Title+'"><img src="'+val.Thumbnail.Url+'" alt="" height="125px" width="100%"></a></div></li>');
    //          }
    //          else {
    //              items.push('<div class="item"><ul class="thumbnails"><li class="span3"><div class="thumbnail"><a class="fancybox" href="'+val.MediaUrl+'" title="'+val.Title+'"><img src="'+val.Thumbnail.Url+'" alt="" height="125px" width="100%"></a></div></li>');
    //          }
    //      }
    //      else if (index%4 !== 3){
    //          items.push('<li class="span3"><div class="thumbnail"><a class="fancybox" href="'+val.MediaUrl+'" title="'+val.Title+'"><img src="'+val.Thumbnail.Url+'" alt="" height="125px" width="100%"></a></div></li>');
    //      }
    //      else {
    //          items.push('<li class="span3"><div class="thumbnail"><a class="fancybox" href="'+val.MediaUrl+'" title="'+val.Title+'"><img src="'+val.Thumbnail.Url+'" alt="" height="125px" width="100%"></a></div></li></ul></div>');
    //      }
    //  });
    //  pic_flow.append(items.join('\n'));

    // });


    //Get videos from Youtube
    var youtube_url = 'https://gdata.youtube.com/feeds/api/videos?v=2&alt=jsonc&q='+search+'&max-results=5&format=5&safesearch=strict&callback=?';
    $.getJSON(youtube_url, function(data) {
        var videos = [];
        //$('iframe#videos').attr('src','');
        $.each(data.data.items, function(index, val) {
            var active = (index===1)?' active':'';
            videos.push('<div class="item'+active+'"class="center"><iframe class="youtube-player" id="videos" type="text/html" width="100%" height="500px" src="http://www.youtube.com/embed/'+val.id+'?wmode=transparent" frameborder="0"></iframe></div>');
        });
        //$("iframe").each(function() {
        //  this.contentWindow.postMessage('{ "method": "pause" }', "http://www.youtube.com/embed/'+val.id+'?wmode=transparent");
        //});
        // console.log(videos);
        vid_flow.append(videos.join('\n'));
    });

    load_from_api(search);

    $('img').error(function() {
        $(this).remove();
    });

    //make the video flow not slide automatically

}

$('[id^="video_flow"]').carousel('pause');
$('#picture_flow').carousel();

YUI().use('autocomplete', 'autocomplete-highlighters', function(Y) {
    Y.one('body').addClass('yui3-skin-sam');
    Y.one('#in-field').plug(Y.Plugin.AutoComplete, {
        resultHighlighter : 'phraseMatch',
        resultListLocator: function (response) {
            return (response[1]) || [];
        },
        source: 'https://en.wikipedia.org/w/api.php?action=opensearch&search={query}&limit=10&namespace=0&format=json&callback={callback}'
    });
});

// $('#video_flow a[href="#picture_flow"]').click(function (e){
//  $('iframe#videos').attr('src','');
// });

$('#myTab a[href="#combo"]').click(function (e) {
    e.preventDefault();
    $(this).tab('show');
    $('#video_image_span').show().removeClass("span9").addClass("span7");
    $('#video_flow').show();
    $('#picture_flow').show();
    $('#wiki_text').show().removeClass("span10").addClass("span3");
});

$('#myTab a[href="#youtube"]').click(function (e) {
    e.preventDefault();
    $(this).tab('show');
    $('#video_image_span').show().removeClass("span7").addClass("span9");
    $('#video_flow').show();
    $('#picture_flow').hide();
    $('#wiki_text').hide().removeClass("span10").addClass("span3");
});

$('#myTab a[href="#images"]').click(function (e) {
    e.preventDefault();
    $(this).tab('show');
    $('#video_image_span').show().removeClass("span7").addClass("span9");
    $('#video_flow').hide();
    $('#picture_flow').show();
    $('#wiki_text').hide().removeClass("span10").addClass("span3");
});

$('#myTab a[href="#wolfram"]').click(function (e) {
    e.preventDefault();
    $(this).tab('show');
    $('#video_image_span').show();
    $('#video_flow').hide();
    $('#picture_flow').hide();
    $('#wiki_text').hide().removeClass("span10").addClass("span3");
});

$('#myTab a[href="#pdf"]').click(function (e) {
    e.preventDefault();
    $(this).tab('show');
    $('#video_image_span').show();
    $('#video_flow').hide();
    $('#picture_flow').hide();
    $('#wiki_text').hide().removeClass("span10").addClass("span3");
});

$('#myTab a[href="#SWF"]').click(function (e) {
    e.preventDefault();
    $(this).tab('show');
    $('#video_image_span').show();
    $('#video_flow').hide();
    $('#picture_flow').hide();
    $('#wiki_text').hide().removeClass("span10").addClass("span3");
});

$('#myTab a[href="#wikipedia"]').click(function (e) {
    e.preventDefault();
    $(this).tab('show');
    $('#video_image_span').hide();
    $('#video_flow').hide();
    $('#picture_flow').hide();
    $('#wiki_text').show().removeClass("span3").addClass("span10");
});
// https://api.datamarket.azure.com/Data.ashx/Bing/Search/Image?Query=%27binary%20search%20tree%27&Market=%27en-US%27&Adult=%27Moderate%27&$top=50&$format=Atom
// http://msdn.microsoft.com/en-us/library/dd250846.aspx
// 9B2B80CDB8B7ED402F4D7D79B8243F25F8A95B2E
// http://api.search.live.net/json.aspx?AppId=5B0D22D739247C06BE7F990ECBEC1A144F9B7C39
//     &Sources=image&Query=prague&Image.Count=10
//     &Image.Offset=0&Image.Filters=Size:Medium
// http://api.search.live.net/json.aspx?AppId=5B0D22D739247C06BE7F990ECBEC1A144F9B7C39&Sources=image&Query=prague&Image.Count=3&Image.Offset=0&Image.Filters=Size:Medium


// http://en.wikipedia.org/wiki/Special:Export/LinkedIn
// http://www.mediawiki.org/wiki/API#A_simple_example
// http://www.mediawiki.org/wiki/API:Query>>>>>>> other

//Youtube
//Developer Key: AI39si5VIAdPPeexdPxRg9SHTOdNrUAvqHmq-GW6KFB26B_YCKSyGvNDdc9nEK8LH-a8NOKnJWbZvdejZlwp8gKgfV2qA078dw

//$('#element').youTubeEmbed('http://www.youtube.com/watch?v=u1zgFlCw8Aw');
// Or:
//$('#element').youTubeEmbed({
//  video           : 'http://www.youtube.com/watch?v=u1zgFlCw8Aw',
//  width           : 600,      // Height is calculated automatically
//  progressBar : false     // Hide the progress bar
//});

//Wolfram
//APPID(from other people): QKVJ42-7UX5XLE9AT
//(applied by myself):
//  UQJRUU-XAE263JGR5
//  UQJRUU-QVWHEHR4J7
//  UQJRUU-L2QP92GWY9
//  UQJRUU-L5A9PJLXEQ
//  UQJRUU-H95AUX22UX
//  UQJRUU-5KW92HUQ5K
//  UQJRUU-RG3T6KHHL4
//  UQJRUU-ETY9VGVRP3
//  UQJRUU-RLW7EXRXAP
//  UQJRUU-HYXPX23J2J
//var key = Wub_GetVaultValue("wolframalphakey") ? nil;
//var res = nil;
//var format = "";
//if key != nil then
//   format = "&format=plaintext";
//   var P = GetURL("http://api.wolframalpha.com/v1/query?input=" + query + "&appid=" + key + format);

//http://api.wolframalpha.com/v2/query?input=pi&appid=XXXX
//url="http://api.wolframalpha.com/v2/query?input=GF("+str(n)+")&appid="+app+"&format=plaintext&includepodid=AdditionTable&includepodid=MultiplicationTable"
// http://stackoverflow.com/questions/9745746/twitter-bootstrap-2-carousel-display-a-set-of-thumbnails-at-a-time-like-jcarou
// http://jsfiddle.net/andresilich/S2rnm/show/
// http://finnrudolph.de/ImageFlow/Installation
// https://github.com/reddit/reddit/wiki/API