
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
     *  Code common to both jupman in jupyter and Website
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
     *   Jupyter only instructions - doesn't run on website
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
    * Website only instructions
    */
    initWebsite : function(){  
        
        console.log("initializing jupman.js in Website ...")
        
        console.log("Fixing menu clicks for https://github.com/DavidLeoni/jupman/issues/38")

        // function copied as is from
        // https://github.com/readthedocs/sphinx_rtd_theme/blob/master/src/theme.js#L190
        var toggleCurrent = function (elem) {
            var parent_li = elem.closest('li');
            parent_li.siblings('li.current').removeClass('current');
            parent_li.siblings().find('li.current').removeClass('current');
            parent_li.find('> ul li.current').removeClass('current');
            parent_li.toggleClass('current');
        }        

        
        var fix = function(prefix){

            s = 'a.reference.internal[href^="' + prefix + 'toc.html"]'

            // DIRTY: THIS IS A POTENTIAL BUG: IF 'index' is not the last one it won't be selected !
           //  Made so because index may be translated in other languages   

            var link = $(s).not(":last")
            var span = $(s + ' > span');
            span.off('click')

            link.on('click', function (ev) {
                ev.preventDefault();
                toggleCurrent($(this));
                ev.stopPropagation();
                return false;
            });
        }

        fix('')
        fix('../')
        fix('../../')    // probably useless but just in case ...
        fix('../../../') // probably useless but just in case ... 

        console.log("Fixing Python Tutor overflow ...");

        // need it in js as there are no css parent selectors.
        // NOTE: these selectors are different from Jupyter ones !!!
        var pytuts = $('.pytutorVisualizer')        
        pytuts.closest('div.output_area.rendered_html.docutils.container')
              .css('overflow', 'visible')
        
        jupman.initWebsiteLangs();

        console.log("Finished initializing jupman.js in website")
    },
    
    /** Displays flags on SoftPython website
     * 
     */
    initWebsiteLangs : function(){
        if (!window.JUPMAN_LANG){
            console.log("No JUPMAN_LANG defined, skipping initWebsiteLangs");
            return;
        }
        var page = window.location.pathname;
        if (window.location.protocol =='file:'){
            var prefix_pos = page.indexOf('_build/html/');
            if (prefix_pos != -1){
                page = page.slice(prefix_pos + '_build/html/'.length);
            }
        } 
        xhr.open("GET", "https://en.softpython.org/cgi-bin/lang.php?page="+page, true);
        xhr.onload = function (e) {
            if (xhr.readyState === 4) {
                if (xhr.status === 200) {
                    console.log(xhr.responseText);
                    var trans = JSON.parse(xhr.responseText);
                    var the_div = document.getElementById("jupman-langs");
                    the_div.textContent = '';
                    for (var lang in trans) {
                        if (lang != JUPMAN_LANG){                        
                            var link_node = document.createElement("A");
                            link_node.setAttribute('href',trans[lang]);
                            link_node.setAttribute('title','Switch language to ' + lang.toUpperCase());
                            var img_node = document.createElement('IMG');
                            img_node.setAttribute('src','_static/img/flags/flat/32/'+lang+'.png');
                            img_node.setAttribute('alt',lang.toUpperCase());
                            link_node.appendChild(img_node);
                            the_div.appendChild(link_node);
                        }
                    }
                } else {
                    console.error(xhr.statusText);
                    console.log(xhr.responseText);
                }
            }
        };
        xhr.onerror = function (e) {
            console.error(xhr.statusText);
            console.log(xhr.responseText);
        };
        xhr.send(null);           
    },
    
    /**
     * Initializes jupman.js
     */
    init : function(){

       jupman.initCommon();
        
       if (typeof JUPMAN_IN_JUPYTER === "undefined" || !JUPMAN_IN_JUPYTER ){            
           jupman.initWebsite();
       } else {
           jupman.initJupyter();
       }
        
    }
}

$(document).ready(jupman.init);
