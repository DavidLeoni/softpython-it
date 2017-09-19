
/*
 * JUPYTER MANAGER JavaScript https://github.com/DavidLeoni/jupman 
 * 
 */

function showthis(url) {
    window.open(url, "pres", "toolbar=yes,scrollbars=yes,resizable=yes,top=10,left=400,width=500,height=500");
    return(false);
}

var jupman = {
    
    isReduced : function(){
        return $(window).width() < 924;
    },
    hoverToc : function(){
        return $('#jupman-toc:hover').length != 0;
    },
    resize : function(){
        if (jupman.isReduced()){
            $("#jupman-toc").hide();
        } else {
            $("#jupman-toc").show();
            $("#jupman-toc").css("background","rgba(255, 255, 255, 0)");
            
            tocParams = {
                
                'selectors': 'h1,h2,h3', //elements to use as headings
                'container': 'body', //element to find all selectors in
                'smoothScrolling': true, //enable or disable smooth scrolling on click
                 //doesn't work  'prefix': 'jupman-toc', //prefix for anchor tags and class names
                //'onHighlight': function(el) {}, //called when a new section is highlighted 
                'highlightOnScroll': true, //add class to heading that is currently in focus
                'highlightOffset': 100, //offset to trigger the next headline
                'anchorName': function(i, heading, prefix) { //custom function for anchor name
                    return prefix+i;
                },
                'headerText': function(i, heading, $heading) { //custom function building the header-item text                  
                    return $heading.text().replace("¶","");
                },
                'itemClass': function(i, heading, $heading, prefix) { // custom function for item class
                    return $heading[0].tagName.toLowerCase();
                }                
            }
            
            $('#jupman-toc').toc(tocParams);
        }
    },
    /**
        Hides cell input
        
        Renamed in 0.19
    */    
    hideCell : function(prefixOrRegex){
        
        $('.border-box-sizing .code_cell pre').filter(function() { 
                var t = $(this).text();
                if (typeof prefixOrRegex == "string"){
                    return t.indexOf(prefixOrRegex) === 0;
                } else if ( prefixOrRegex instanceof RegExp){
                    return t.match(prefixOrRegex);
                } else {
                    console.error("Invalid argument:", prefixOrRegex);
                    throw new Error("Invalid argument!");
                }
            }).parents('div .cell .input').hide();        
    },
    /**
        Hides the cell input AND output.
        
        @since 0.19
    */
    hideCellAll : function(prefix){        
        $('.border-box-sizing .code_cell pre').filter(function() { 
                return $(this).text().indexOf(prefix) === 0; 
            }).parents('div .cell ').hide();        
    },
    
    init : function(){

       var toc = $("<div>").attr("id", "jupman-toc");              
       var indexLink = $("<a>")
                        .addClass("jupman-nav-item")
                        .attr("href","index.html#Chapters")
                        .text("jupman");
       
       
       
       var candidateTitleText = $(".jupman-title").text();              
                                  
                    
       
       var nav = $("<div>")
                     .attr("id", "jupman-nav")
                    .append(indexLink);       
       
       if (candidateTitleText.length !== 0){

           var title = $("<span>")
                    .addClass("jupman-nav-item")
                    .css("padding-left","8px")
                    .text(candidateTitleText);
            nav.append("<br>")
                .append("<br>")
                .append(title);                                
        }
                     
       // TODO THIS HIDE STUFF DOES NOT WORK ANYMORE AFTER PORTING TO NBSPHINX 
       // INSTEAD, YOU SHOULD EDIT 
       jupman.hideCell("%%HTML");
       jupman.hideCell("import jupman");   
       
        // TODO this is a bit too hacky   
       jupman.hideCell(/from exercise(.+)_solution import \*/)
       
       jupman.hideCell("jupman.init()"); 
       jupman.hideCell("jupman.show_run(");
       jupman.hideCell("nxpd.draw(");
       jupman.hideCellAll("jupman.run("); 
              
       if ($("#jupman-toc").length === 0){
           $("body").append(toc);       
       } else {
           $("#jupman-toc").replaceWith(toc);
       }
       
       if ($("#jupman-nav").length === 0){
           $("body").append(nav);       
       } else {
           $("#jupman-nav").replaceWith(nav);
       }              
       
       jupman.resize();
    }
}

$( window ).resize(function() {
    jupman.resize();
});


$("body").on("mousemove",function(event) {
    if (jupman.isReduced()){
        if (event.pageX < 50) {            
             $("#jupman-toc").show(); 
            $("#jupman-toc").css("background","rgba(255, 255, 255, 1.0)");
        } else {
            
            if (jupman.hoverToc()) {                    
            } else {
                $("#jupman-toc").hide();                        
            }
                     
/*            if ($("#jupman-toc").is(":visible")){
                if (jupman.hoverToc()) {                    
                } else {
                    $("#jupman-toc").hide();                        
                }
            } else {
                if (jupman.hoverToc())
                  show
              } else {
                $("#jupman-toc").hide();                        
               }                 
            }
  */     
        }
    }
});

$(document).ready(jupman.init);
