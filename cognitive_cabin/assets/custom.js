$(document).ready(function(){
    $("#on_off").click(function(){
        $(".mainContent .showContentPlacer").fadeOut("slow", function(){
            $(".mainContent .offPlaceholder").fadeIn("slow");
        });
    });

    $(".mainContent, .bottomButton").click(function(){
        $(".mainContent .offPlaceholder").fadeOut("slow", function(){
            $(".mainContent .showContentPlacer").fadeIn("slow");
        });
    });
});
