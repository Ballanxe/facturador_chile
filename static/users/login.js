/*
    Function to make login in ajax
    @param e Recives event
    @param element Recives trigger element
*/
function login(e,element){
    e.preventDefault();
    var form = $(element).parent().parent();
    if(login_validate(form)){
        $.ajax({
            data: $(form).serialize(), 
            type: 'POST',
            url: $(form).attr('action'),
            success: function(response) {
                if (response.validate) {
                    $('#id_contrasena_validate').val($(form).find('#id_contrasena').val());
                    $('#id_usuario_validate').val($(form).find('#id_usuario').val());
                    var first_item = $('.carousel-inner .item')[0];
                    $('#myCarousel').carousel('next');
                    $('.span-min').html(response.time/60);
                    $('.span-sec').html('00');
                    
                    setTimeout(login_validate_counter(response.time),1000);
                    
                }
                else{
                    $.each($(form).find('input'),function(key,value){
                        $(value).addClass("has-error");
                        var error_container = $(value).parent().find('.errors');
                        $(error_container).html(response.msg);
                    });
                }
            }
            });
    }
}


/*
    Function to go check login time
    @param time Recives time object
*/
function login_validate_counter(time){
    timerId = setInterval(function(){
        if($('.span-sec').html()=='00'){
            $('.span-sec').html(59);
            $('.span-min').html(parseInt($('.span-min').html())-1);
        }
        else{
            var number = parseInt($('.span-sec').html())-1;
            if(number<10){
                number = '0'+number
            }
            $('.span-sec').html(number);
        }
        if($('.span-min').html()=='0' && $('.span-sec').html()=='00'){
            clearInterval(timerId);
            $('.resend_button').show();
            $('.validate_button').hide();
        }
    },1000);

}


/*
    Function to go back on login
    @param form Recives element object
*/
function backlogin(element){
    $('#myCarousel').carousel('prev');
    clearInterval(timerId);
    delete timerId;
}

/*
    Function to resend code
    @param e Recives event
    @param element Recives trigger element
*/
function resend(e,element){
    clearInterval(timerId);
    delete timerId;
    $('.resend_button').hide();
    $('.validate_button').show();
    e.preventDefault();
    var form = $('#second_login form');
    $.ajax({
    data: $(form).serialize(), 
    type: 'POST',
    url: URL_LOGIN,
    success: function(response) {
        if (response.validate) {
            $('.span-min').html(response.time/60);
            $('.span-sec').html('00');
            setTimeout(login_validate_counter(response.time),1000);
        }
    }
    });
}


/*
    Function to make validate code in ajax
    @param e Recives event
    @param element Recives trigger element
*/
function validate_code(e,element){
    e.preventDefault();
    var form = $(element).parent().parent();
    if(login_validate(form)){
        $.ajax({
        data: $(form).serialize(), 
        type: 'POST',
        url: $(form).attr('action'),
        success: function(response) {
            if (!response.validate) {
                var error_container = $(form).find('#id_serial_validate').parent().find('.errors');
                $(error_container).html(response.msg);
            }
            else{
                $(location).attr('href', response.url_redirect);
            }
        }
        });
    }
}

/*
    Function to validate login related inputs
    @param form Recives form object
*/
function login_validate(form){
    var valid = true;
    $.each($(form).find('input'),function(key,value){
        if($(value).val()==''){
            valid = false;
            $(value).addClass("has-error");
            var error_container = $(value).parent().find('.errors');
            $(error_container).html('This field is required');
        }
        else{
            $(value).removeClass("has-error");
        }
    });
    return valid;   
}