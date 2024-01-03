// user starts on loading page and will be redirected to the main page automatically
$(document).ready(function(){
    $.ajax({
        type: 'POST',
        url: "/loading",
        success: loadMainPage
    });
  });

// once the classifier has been loaded, the main page should appear
function loadMainPage() {
    location.replace("/analyser")
}