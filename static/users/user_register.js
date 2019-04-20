$(document).ready(function() {
    $("#id_is_staff").on("change", function(){
        if ($('#id_is_staff').is(':checked')){
            $.each([1], function(i,e){
                $("#id_groups option[value='" + e + "']").prop("selected", true);
            });
        }
        else{
            $.each([1], function(i,e){
                $("#id_groups option[value='" + e + "']").prop("selected", false);
            });   
        }
    });
    $('#meter').entropizer({
                target: '#id_password1',
                update: function(data, ui) {
                    ui.bar.css({
                        'background-color': data.color,
                        'width': data.percent + '%'
                    });
                }
            });
});
