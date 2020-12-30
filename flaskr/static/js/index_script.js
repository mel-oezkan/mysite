$(document).ready(function() {
    $('form').on('submit', function(event) {
 
      $.ajax({
        data : {
          from_t   : $('#TimeFromInput').val(),
          to_t     : $('#TimeToInput').val(),
          subject  : $('#SubjectInput').val(),
          place    : $('#PlaceInput').val(),
          maxPeople: $('#ParticipantInput').val()
        },
        type : 'POST',
        url : {{ url_for('study.process')|tojson|safe }}
      })
      .done(function(data) {
 
        if (data.error) {
          $('#errorAlert').text(data.error).show();
          $('#successAlert').hide();
        }
        else {
          // $('#successAlert').text(data.name).show();
          $('#errorAlert').hide();
 
          $(".new-event").css("display", "none");
          $("#add-btn").css("display", "block");  
        }
 
    });
 
 
 
 
    event.preventDefault();
    });
 
 
    $('#add-btn').click(function() {
      $(".new-event").css("display", "block");
      $("#add-btn").css("display", "none"); 
    });
  });