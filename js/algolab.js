
function showthis(url) {
    window.open(url, "pres", "toolbar=yes,scrollbars=yes,resizable=yes,top=10,left=400,width=500,height=500");
    return(false);
}

var algolab = {
    
    isReduced : function(){
        return $(window).width() < 924;
    },
    hoverToc : function(){
        return $('#algolab-toc:hover').length != 0;
    },
    resize : function(){
        if (algolab.isReduced()){
            $("#algolab-toc").hide();
        } else {
            $("#algolab-toc").show();
            $("#algolab-toc").css("background","rgba(255, 255, 255, 0)");
            
            tocParams = {
                
                'selectors': 'h1,h2,h3', //elements to use as headings
                'container': 'body', //element to find all selectors in
                'smoothScrolling': true, //enable or disable smooth scrolling on click
                 //doesn't work  'prefix': 'algolab-toc', //prefix for anchor tags and class names
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
            
            $('#algolab-toc').toc(tocParams);
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

       var toc = $("<div>").attr("id", "algolab-toc");              
       var indexLink = $("<a>")
                        .addClass("algolab-nav-item")
                        .attr("href","index.html#Chapters")
                        .text("Algolab");
       
       
       
       var candidateTitleText = $(".algolab-title").text();              
                                  
                    
       
       var nav = $("<div>")
                     .attr("id", "algolab-nav")
                    .append(indexLink);       
       
       if (candidateTitleText.length !== 0){

           var title = $("<span>")
                    .addClass("algolab-nav-item")
                    .css("padding-left","8px")
                    .text(candidateTitleText);
            nav.append("<br>")
                .append("<br>")
                .append(title);                                
        }
                     
       
       algolab.hideCell("%%HTML");
       algolab.hideCell("import algolab");   
       
        // TODO this is a bit too hacky   
       algolab.hideCell(/from exercise(.+)_solution import \*/)
       
       algolab.hideCell("algolab.init()"); 
       algolab.hideCell("algolab.show_run(");
       algolab.hideCell("nxpd.draw(");
       algolab.hideCellAll("algolab.run("); 
              
       if ($("#algolab-toc").length === 0){
           $("body").append(toc);       
       } else {
           $("#algolab-toc").replaceWith(toc);
       }
       
       if ($("#algolab-nav").length === 0){
           $("body").append(nav);       
       } else {
           $("#algolab-nav").replaceWith(nav);
       }              
       
       algolab.resize();
    }
}

$( window ).resize(function() {
    algolab.resize();
});


$("body").on("mousemove",function(event) {
    if (algolab.isReduced()){
        if (event.pageX < 50) {            
             $("#algolab-toc").show(); 
            $("#algolab-toc").css("background","rgba(255, 255, 255, 1.0)");
        } else {
            
            if (algolab.hoverToc()) {                    
            } else {
                $("#algolab-toc").hide();                        
            }
                     
/*            if ($("#algolab-toc").is(":visible")){
                if (algolab.hoverToc()) {                    
                } else {
                    $("#algolab-toc").hide();                        
                }
            } else {
                if (algolab.hoverToc())
                  show
              } else {
                $("#algolab-toc").hide();                        
               }                 
            }
  */     
        }
    }
});

$(document).ready(algolab.init);
