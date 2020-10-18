
/**
 * JUPYTER MANAGER JavaScript https://github.com/DavidLeoni/jupman 
 * 
 */


/**
 * @deprecated use jupman.toggleVisibility instead
 * @param {string} what 
 */
function toggleVisibility(what){
    console.warn("global toggleVisibility is deprecated, use jupman.toggleVisibility instead");
    jupman.toggleVisibility(what);            
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
   
    /**
     * NOTE: ONLY WORKS ON THE WEBSITE
     *      
     * @param {@string} caller a this from html tag onclick
     * @since 3.2 
     */
    toggleSolution : function(caller){
        
        let toggler = $(caller);
        let content = toggler.next();
        
        content.addClass('jupman-sol jupman-sol-content');        

        if (content.css('display') === 'none'){            
            toggler.text(toggler.data('jupman-hide'));
        } else {                                    
            toggler.text(toggler.data('jupman-show'));            
        }
        content.slideToggle();                                
    },
    
    /**
     * Simple vanilla way to toggle an element
     * @param {string} what i.e. someid (no # prefix)
     */
    toggleVisibility : function (what){

        var e = document.getElementById(what);
        if(e.style.display == 'block') {
            e.style.display = 'none';
        } else {
            e.style.display = 'block';        
        }
    },

    /**
     *  Code common to both jupman in jupyter and Website
    */
    initCommon : function(){
        
        console.log('jupman.js initCommon start')
        
        console.log("jupman.js Initializing togglable stuff");
        if (typeof $ == "undefined"){
            console.error("   No jquery found! Skipping ... ");
        } else {
                        
            console.log("Initializing generic jupman-togglable stuff");

            let defaultShowMsg = 'Show';
            let defaultHideMsg = 'Hide';            

            $(".jupman-toggler").remove();
            
            $(".jupman-togglable").each(function(index, value) {
                let toggler = $('<a href="#"></a>');
                toggler.addClass('jupman-toggler');
                let showMsg = defaultShowMsg;            
                if ($(this).data('jupman-show')){
                    showMsg = $(this).data('jupman-show');
                }
                
                toggler.text(showMsg);
                toggler.insertBefore(value);
            });            
            
            $(".jupman-togglable").hide();
            $(".jupman-toggler").show();

            $('.jupman-toggler')
                .off('click')
                .click(function(ev){                                
                    let toggler = $(this);
                    
                    let uls = toggler.nextAll(".jupman-togglable");
                    let sibling = uls.eq(0);
                    
                    let showMsg = defaultShowMsg;
                    let hideMsg = defaultHideMsg;
                    if (sibling.data('jupman-show')){
                        showMsg = sibling.data('jupman-show');
                    }
                    if (sibling.data('jupman-hide')){
                        hideMsg = sibling.data('jupman-hide');
                    }
                    if (sibling.css('display') === 'none'){            
                        toggler.text(hideMsg);
                    } else {                                    
                        toggler.text(showMsg);
                    }
                    sibling.slideToggle();        
                    ev.preventDefault();
                    ev.stopPropagation();
                    return false;
            });
        } 
        console.log('jupman.js initCommon end')

    },

    /**
     *   Jupyter only instructions - doesn't run on website
     */
    initJupyter : function(){
       console.log('jupman.js initJupyter start') 

       var toc = $("<div>").attr("id", "jupman-toc");              
                                                             
       var nav = $("<div>")
                     .attr("id", "jupman-nav")
                    
        
        
       // ****************************     WARNING      ********************************
       //         THIS HIDE STUFF DOES NOT WORK IN SPHINX, ONLY WORKS WHEN YOU MANUALLY EXPORT TO HTML 
       // ******************************************************************************
       
       
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
$
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
       console.log('jupman.js initJupyter end')
    },
    
    /**
    * Website only instructions
    */
    initWebsite : function(){  
        
        console.log("jupman.js initWebsite start")
        
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

        console.log("jupman.js initWebsite end")
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
