
softpython = {

/** Displays flags on SoftPython website
     * 
     */
    initWebsiteLangs : function(){

        console.log("softpython.js initWebsiteLangs start");

        if (!window.JUPMAN_LANG){
            console.log("No JUPMAN_LANG defined, skipping initWebsiteLangs");
            return;
        }
        var page = window.location.pathname;
        var imgPrefix = '/'
        if (window.location.protocol =='file:'){
            var prefix_pos = page.indexOf('_build/html/');
            if (prefix_pos != -1){
                page = page.slice(prefix_pos + '_build/html/'.length);
                imgPrefix = window.location.pathname.slice(0,prefix_pos);
            }

        }
        let xhr = new XMLHttpRequest();
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
                            img_node.setAttribute('src',imgPrefix + '_static/img/flags/flat/32/'+lang+'.png');
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
        console.log("softpython.js initWebsiteLangs end");
     }

}


$(document).ready(softpython.initWebsiteLangs);