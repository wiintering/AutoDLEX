
$(document).ready(function(){
        $("#profile_image").change(function(){
            if (this.files.length > 0) {
                var imageFileType = this.files[0].type;
                var match = ["image/jpeg", "image/png", "image/gif", "image/jpg"];
    
                if (!(match.includes(imageFileType))) {
                    swal({
                        title: "Invalid Image File",
                        text: "Please select a valid image file (JPEG/PNG/GIF/JPG)",
                        icon: "error",
                        button: "OK"
                    }).then(function() {
                        $('#profile_image').val('');
                    });
                    return false;
                }
            }
        });
    });


    const selectBtn = document.querySelector(".select-btn"),
    items = document.querySelectorAll(".item");

selectBtn.addEventListener("click", () => {
  selectBtn.classList.toggle("open");
});

items.forEach(item => {
  item.addEventListener("click", () => {
      item.classList.toggle("checked");

      let checked = document.querySelectorAll(".checked"),
          btnText = document.querySelector(".btn-text");

          if(checked && checked.length > 0){
              btnText.innerText = `${checked.length} Selected`;
          }else{
              btnText.innerText = "Select Language";
          }
  });
})
