
$(document).ready(function(){
    // feed in user input for evaluation, eventually update visuals
    $("#submit").click(function (event) {
        $.ajax({
            type: 'POST',
            url: "/runAnalytics",
            data: {param: $("#queryText").val()},
            success: visualizeResults
        });
    });

    // clear all input and feedback
    $("#reset").click(function (event) {
        // reset input prompt
        $("#queryText").val("");

        // reset summary
        $("input:text").attr("placeholder", "Inspection");

        // quick-hack to reset the visuals
        for (let catid = 0; catid <= 100; ++catid) {
            $("#estimate-" + catid).attr("class", "btn btn-outline-secondary");
        }
    });

    // place an example message
    $("#demo").click(function (event) {
        $.ajax({
            type: 'POST',
            url: "/demo",
            success: placeDemoMessage
        });
    });
    $("#estimate-visuals-block").hide();


    $("#insights").click(function (event) {
    location.replace("/insights");
    })
  });

// updates the user input mask with a demo message
function placeDemoMessage(demoMsg) {
    $("#queryText").val(demoMsg);
}

// callback function after the estimator provided evaluation results
function visualizeResults(response) {

    // categories is a '<category>:[[<probabilities>]],'-like string. e.g. 'electricity:[[0.9 0.1]], tools:[[0.99 0.01]],' 
    let categories = response.split(",")
    let catid = 0; // visual id
    let summary = "" // covers probability feedback
    // for each category report likeliness
    for (category of categories) {
        let category_items = category.split(":");
        if (category_items.length == 2)
        {
            let category_name = category_items[0];
            let category_proba = category_items[1].replaceAll("[", "").replaceAll("]", "").split(" ")[1];
            let category_feedback;
            if (category_proba > 0.8) // very likely --> mark green
            {
                summary += " " + category_name + " " + category_proba * 100 + " %";
                category_feedback = "btn btn-success"
            }
            else if (category_proba > 0.5) // unsure --> mark yellow
            {
                summary += " " + category_name + " " + category_proba * 100 + " %";
                category_feedback = "btn btn-warning"
            }
            else // otherwise unrelevant
            {
                category_feedback = "btn btn-outline-secondary"
            }

            $("#estimate-" + catid).attr("class", category_feedback);
        }
        catid ++;
    }
    if (summary.length == 0) // if nothing could be identified it's probably unrelated
    {
        summary = "Not relevant"
    }
    $("input:text").attr("placeholder", summary);
    $("#estimate-visuals-block").show();
}