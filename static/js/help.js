$(document).ready(function(){
    $(document).on("click", ".sidemenu .help-menu-option", function(){
        id = $(this).attr("id");
        button = $(this);

        $(".help-content div").each(function(){
            console.log("in");
            console.log($(this).attr("id"));
            if ($(this).attr("id") == id + "_content"){
                // This is the one
                $(this).removeClass('d-none');
            }
            else{
                // The rest
                $(this).addClass('d-none');
            }
        });

        $(".sidemenu .help-menu-option").each(function(){
            if ($(this).attr("id") != id)
                $(this).css("background-color", "#919b74");
            else
                $(this).css("background-color", "#565c45");
        })
    });
});