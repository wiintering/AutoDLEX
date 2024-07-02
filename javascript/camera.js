(function() {
    var width = 700; // Increase the width for higher resolution
    var height = 480; // Increase the height for higher resolution
    var streaming = false;
    var video = null;
    var canvas = null;
    var photo = null;
    var startbutton = null;
    var retakebutton = null; // Reference to the retake button
    var extractedTextElement = null; // Reference to the div to display extracted text
    var capturedImageElement = null; // Reference to the img element to display captured image
    var submit = document.getElementById('submit'); // Reference to the submit button

    function startup() {
        video = document.getElementById('video');
        canvas = document.getElementById('canvas');
        photo = document.getElementById('photo');
        startbutton = document.getElementById('startbutton');
        retakebutton = document.getElementById('retakebutton'); // Get the reference to retake button
        extractedTextElement = document.getElementById('extractedText'); 
        capturedImageElement = document.getElementById('capturedImage');

        navigator.mediaDevices.getUserMedia({
            video: true,
            audio: false
        })
        .then(function(stream) {
            video.srcObject = stream;
            video.play();
            submit.disabled = true;
          
        })
    
        .catch(function(err) {
            console.log("An error occurred: " + err);
        });

     

        video.addEventListener('canplay', function(ev) {
            if (!streaming) {
                height = video.videoHeight / (video.videoWidth / width);

                if (isNaN(height)) {
                    height = width / (4 / 3);
                }

                video.setAttribute('width', width);
                video.setAttribute('height', height);
                canvas.setAttribute('width', width);
                canvas.setAttribute('height', height);
                streaming = false;
            }
        }, false);

        startbutton.addEventListener('click', function(ev) {
            takepicture();
            ev.preventDefault();
        }, false);

        retakebutton.addEventListener('click', function(ev) {
            retakephoto();
            ev.preventDefault();
        }, false);

        clearphoto();
    }

    function clearphoto() {
        var context = canvas.getContext('2d');
        context.fillStyle = "#AAA";
        context.fillRect(0, 0, canvas.width, canvas.height);
        var data = canvas.toDataURL('image/png');
        photo.setAttribute('src', data);
       
    }

    function takepicture() {
        var context = canvas.getContext('2d');
        if (width && height) {
            canvas.width = width;
            canvas.height = height;
            context.drawImage(video, 0, 0, width, height);

            // Serialize the image data
            var dataURL = canvas.toDataURL('image/png');
            var blobBin = atob(dataURL.split(',')[1]);
            var array = [];
            for(var i = 0; i < blobBin.length; i++) {
                array.push(blobBin.charCodeAt(i));
            }
            var file = new Blob([new Uint8Array(array)], { type: 'image/png' });
            var formData = new FormData();
            formData.append('image', file, 'image.png');
            fetch('/process_image', {
                method: 'POST',
                body: formData
            })
            .then(response => response.text())
            .then(text => {
                // Display extracted text
                extractedTextElement.textContent = text;
                // Display the processed image
                capturedImageElement.src = dataURL;
                capturedImageElement.style.display = 'block'; // Make the processed image visible
                retakebutton.style.display = 'block'; // ShowA the "Retake" button
                video.style.display = 'none'; // Hide the video stream
                submit.disabled = false;
                
            })
            .catch(error => console.error('Error:', error));
        } else {
            clearphoto();
        }
    }

    function retakephoto() {
        capturedImageElement.style.display = 'none'; // Hide the captured image
        startbutton.style.display = 'block'; // Show the "Take photo" button
        video.style.display = 'inline-block'; // Show the video stream
        submit.disabled = true;
    }

    window.addEventListener('load', startup, false);
})();
