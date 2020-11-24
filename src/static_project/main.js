$(document).ready(function () {
  console.log("Working...");
  $("#modal-btn").click(function () {
    $(".ui.modal").modal("show");
  });
  $(".ui.dropdown").dropdown();
});
