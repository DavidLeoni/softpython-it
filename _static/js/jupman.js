
/*
 * JUPYTER MANAGER JavaScript https://github.com/DavidLeoni/jupman 
 * 
 */

function toggleVisibility(what){
        var e = document.getElementById(what);
        if(e.style.display == 'block')
          e.style.display = 'none';
        else
          e.style.display = 'block';
    };
    

function showthis(url) {
    window.open(url, "pres", "toolbar=yes,scrollbars=yes,resizable=yes,top=10,left=400,width=500,height=500");
    return(false);
}

var jupman = {
    
    /** 
        Checks if toc was injected in the script. 
    */
    hasToc : function(){
        return $('#jupman-toc').toc;
    },
    
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
            
            if (jupman.hasToc()){
                $('#jupman-toc').toc(tocParams);
            }
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
    hideCellAll : function(prefixOrRegex){        
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
            }).parents('div .cell ').hide();        
    },
    
    toggleVisibility: function(what){
        var e = document.getElementById(what);
        if(e.style.display == 'block')
          e.style.display = 'none';
        else
          e.style.display = 'block';
    },
    
    /**
     *  Code common to both jupman in jupyter and ReadTheDocs
    */
    initCommon : function(){
        
        $(".jupman-solution-header").remove();
        span = $('<div>');
        span.addClass('jupman-solution-header');
        span.text('Show/hide solution');
        
        span.insertBefore(".jupman-solution");
        
        
        $(".jupman-solution").hide();
        $(".jupman-solution-header").show();

        $('.jupman-solution-header')
            .off('click')
            .click(function(){
                
                var uls = $(this).nextAll(".jupman-solution");             
                var sibling = uls.eq(0);
                          
                sibling.slideToggle();        
                ev.preventDefault();
                ev.stopPropagation();
        });

    },

    /**
     *   Jupyter only instructions - doesn't run on ReadTheDocs
     */
    initJupyter : function(){
        
       var toc = $("<div>").attr("id", "jupman-toc");              
                                                             
       var nav = $("<div>")
                     .attr("id", "jupman-nav")
                    
        
        
       // ****************************     WARNING      ********************************
       //         THIS HIDE STUFF DOES NOT WORK IN SPHINX, ONLY WORKS WHEN YOU MANUALLY EXPORT TO HTML 
       // ******************************************************************************
       jupman.hideCell("%%HTML");
       jupman.hideCell("import jupman");
       
        // TODO this is a bit too hacky   
       jupman.hideCell(/from exercise(.+)_solution import \*/)
       
       jupman.hideCellAll(/.*jupman_init.*/); 
       jupman.hideCell("jupman_show_run(");
       jupman.hideCell("nxpd.draw(");
       jupman.hideCellAll("jupman_run("); 
       
       if (jupman.hasToc()){
           if ($("#jupman-toc").length === 0){
               $("body").append(toc);       
           } else {
               $("#jupman-toc").replaceWith(toc);
           }
       } else {
           $("#jupman-toc").hide();
       }
       
       if ($("#jupman-nav").length === 0){
           $("body").append(nav);       
       } else {
           $("#jupman-nav").replaceWith(nav);
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
 
        
       jupman.resize();
       console.log("Finished initializing jupman.js in Jupyter Notebook.")
    },
    
    /**
    * RTD only instructions
    */
    initReadTheDocs : function(){  
        
        console.log("Finished initializing jupman.js in ReadTheDocs")        
    },
    
    /**
     * Initializes jupman.js
     */
    init : function(){

       jupman.initCommon();
        
       if (typeof JUPMAN_IN_JUPYTER === "undefined" || !JUPMAN_IN_JUPYTER ){            
           jupman.initReadTheDocs();
       } else {
           jupman.initJupyter();
       }
        
    }
}

$(document).ready(jupman.init);
