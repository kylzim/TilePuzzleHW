document.addEventListener('DOMContentLoaded', function () {
    const imageFileInput = document.getElementById('image_file');
    const imagePreviewContainer = document.getElementById('imagePreviewContainer');
    const imagePreview = document.getElementById('imagePreview');
    const imagePreviewDefaultText = document.querySelector('.image-preview__default-text');

    if (imageFileInput) {
        imageFileInput.addEventListener('change', function () {
            const file = this.files[0];

            if (file) {
                const reader = new FileReader();

                imagePreviewDefaultText.style.display = 'none';
                imagePreview.style.display = 'block';
                imagePreviewContainer.style.borderColor = 'transparent'; // Optional: remove border on preview

                reader.onload = function (e) {
                    imagePreview.setAttribute('src', e.target.result);
                }
                reader.readAsDataURL(file); // Reads the file as a data URL
            } else {
                // No file selected or selection cancelled
                imagePreview.style.display = 'none';
                imagePreviewDefaultText.style.display = 'block';
                imagePreview.setAttribute('src', '#');
                imagePreviewContainer.style.borderColor = '#ddd'; // Optional: restore border
            }
        });
    }
});