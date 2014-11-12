$(document).ready(function() {
    
    //Remember what the original hover color was
    var originalColor = "yellow";
    
    //Panels light up on home navigator   
    $(".panel").hover(
        function() {
            originalColor = $(this).css("background-color");
            $( this ).css("background-color", "yellow");
        }, function() {
            $( this ).css("background-color", originalColor);
        }
    );
       
});




