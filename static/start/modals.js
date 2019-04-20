function perfil_modals(){
  ruta_user = ruta;
  
    $.ajax({
    url: ruta_user,
    type: "GET",
    data: {
    },
    dataType: 'html',
    success: function(data) {
      $('#modal-body').html(data);
    }
  });
}

function modal_user(id_user){
  ruta_user = ruta.split("/")[1]
  ruta_user = "/"+ruta_user + "/" + id_user + "/"
  $.ajax({
    url: ruta_user,
    type: "GET",
    data: {
    },
    dataType: 'html',
    success: function(data) {
      $('#modal-body').html(data);
    }
  });

}
  $("#perfil").click(function(){
    perfil_modals();
  })