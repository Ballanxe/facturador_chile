$(document).ready(function() {
    console.log(user)
   $.ajax({
    url: RECENT_ACTIVITY,
    type: "GET",
    data: {
        user: user
    },
    dataType: 'html',
    success: function(data) {
              console.log(data);
          }

  });
});