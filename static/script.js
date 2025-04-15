function copyCitation() {
    // Gets the HTML element containing the citation HTML
    const citationElement = document.getElementById("citation-output");
    const html = citationElement.innerHTML; // Preserves HTML formatting tags like italics <i> and bold <b>
    const text = citationElement.innerText; // Plain text version for places that don't support formatting

    // Wraps each version in a Blob. This is like a lightweight file in memory.
    // Each blob has data that is used to determine which blob to paste.
    const blobHTML = new Blob([html], { type: "text/html" });
    const blobText = new Blob([text], { type: "text/plain" });

    // Creats a ClipboardItem that holds both formats. Pasted location determines which to use.
    const clipboardItem = new ClipboardItem({
        "text/html": blobHTML,
        "text/plain": blobText
    });

    // Writes item to clipboard, and shows success or error message.
    navigator.clipboard.write([clipboardItem]).then(function() {
        alert("Citation copied with formatting!");
    }, function(err) {
        alert("Failed to copy citation.");
        console.error(err);
    });
}

//############################# START FETCH DOI DATA ############################
function fetchDOIData() {
    // Grabs DOI input field and shows a status message
    const doi = document.getElementById("doi-input").value; 
    document.getElementById("doi-status").innerText = "Looking up DOI..."

    // Sends a POST request to Flask backend with the DOI in JSON format
    fetch("/lookup-doi", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({doi: doi})
    })
    // Parses the response, checks for an error, and updates page accordingly
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            document.getElementById("doi-status").innerText = "Error: " + data.error;
        } else {
            document.getElementById("doi-status").innerText = "DOI data loaded!";

            // If successful, fills in the form with the fetched citation data
            document.querySelector("[name='author']").value = data.author;
            document.querySelector("[name='title']").value = data.title;
            document.querySelector("[name='year']").value = data.year;
            document.querySelector("[name='publisher']").value = data.publisher;
        }
    });
}
//############################# END FETCH DOI DATA ############################


//############################# START FETCH ISBN DATA ############################
function fetchISBNData() {
    // Grabs ISBN input field and shows a status message
    const isbn = document.getElementById("isbn-input").value.trim();
    document.getElementById("isbn-status").innerText = "Looking up ISBN...";

    // Sends a POST request to Flask backend with the ISBN in JSON format
    fetch("/lookup-isbn", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ isbn: isbn })
    })
    // Parses the response, checks for an error, and updates page accordingly
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            document.getElementById("isbn-status").innerText = "Error: " + data.error;
        } else {
            document.getElementById("isbn-status").innerText = "ISBN data loaded!";

            // If successful, fills in the form with the fetched citation data
            document.querySelector("[name='author']").value = data.author;
            document.querySelector("[name='title']").value = data.title;
            document.querySelector("[name='year']").value = data.year;
            document.querySelector("[name='publisher']").value = data.publisher;
        }
    });
}
//############################## END FETCH ISBN DATA #############################


//############################## START FETCH URL DATA #############################
function fetchURLData() {
    // Grabs URL input field and shows a status message
    const url = document.getElementById("url-input").value;
    document.getElementById("url-status").innerText = "Looking up URL...";

    // Sends a POST request to Flask backend with the ISBN in JSON format
    fetch("/lookup-url", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ url: url })
    })
    // Parses the response, checks for an error, and updates page accordingly
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            document.getElementById("url-status").innerText = "Error: " + data.error;
        } else {
            document.getElementById("url-status").innerText = "URL data loaded!";
            document.querySelector("[name='author']").value = data.author;
            document.querySelector("[name='title']").value = data.title;
            document.querySelector("[name='year']").value = data.year;
            document.querySelector("[name='publisher']").value = data.publisher;
            document.querySelector("[name='url']").value = data.url;

        }
    })
    // If successful, fills in the form with the fetched citation data
    .catch(err => {
        document.getElementById("url-status").innerText = "Error fetching data.";
        console.error(err);
    });
}
//############################### END FETCH URL DATA ##############################


//############################## START AUTOFILL FIELD #############################
function showAutofill(type) {

    // hide all fields. Handles smooth transitions from css
    const sections = document.querySelectorAll('.smooth-toggle');
    sections.forEach(section => section.classList.remove('show'));
  
    const selected = document.getElementById(`${type}`);
    if (selected != "") {
      selected.classList.add('show');
    }

    // if field selected, show it. Handles smooth transitions
    if (selected != "") {
        selected.classList.add("show")
    }
}
//############################### END AUTOFILL FIELD ##############################



//############################ START SOURCE TYPE CHANGE ###########################
function sourceTypeChanged(sourceType) {
    const websiteFields = document.getElementById("website_fields");
  
    if (sourceType === "website") {
      websiteFields.classList.add("show");
    } else {
        websiteFields.classList.remove("show");
    }
}
//############################# END SOURCE TYPE CHANGE ############################