

document.addEventListener('DOMContentLoaded', function() {
    const readButton = document.getElementById('readButton');
    console.log("Button clicked1");
    readButton.addEventListener('click', readFileContent);
});

function readFileContent() {
    console.log("Button clicked2");
    const input = document.getElementById('fileInput');
    if (!input) {
        console.error("File input element not found");
        return;
    }

    const files = input.files;
    if (files.length === 0) {
        console.log("No files selected");
        return;
    }

    for (let i = 0; i < files.length; i++) {
        console.log(`File Name: ${files[i].name}`);
        console.log(`File Size: ${files[i].size} bytes`);
        console.log(`File Type: ${files[i].type}`);
        const file = files[i];
        const reader = new FileReader();

        reader.onload = function(event) {
            console.log(`Content of ${file.name}:`);
            console.log(event.target.result);
        };

        reader.readAsText(file);
    }
}