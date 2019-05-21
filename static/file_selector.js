

function sendRequest(req, callBack)
{
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function(){
        if (this.readyState == 4 && this.status == 200) {
            var fixedResponse = xmlhttp.responseText.replace(/\\'/g, "'");
            var data = JSON.parse(fixedResponse);
            var content = data["content"];
            var filename = data["filename"];
            callBack(filename, content);
        };
    };
    xmlhttp.open("POST", '/file_selector', true);
    xmlhttp.setRequestHeader("Content-Type", "application/json");
    xmlhttp.send(JSON.stringify(req));
}


function onClickSelect()
{
    var req = {
        "filename": document.getElementById("filenamelable").textContent,
        "status": "selected",
        "content": document.getElementById("filecontent").value};
    var callback = function(filename, content){
        document.getElementById("filecontent").value = content;
        document.getElementById("filenamelable").innerHTML = filename;
    };
    sendRequest(req, callback);
}

function onClickAbandon()
{
    var req = {
        "filename": document.getElementById("filenamelable").textContent,
        "status": "abandoned",
        "content": document.getElementById("filecontent").value};
    var callback = function(filename, content){
        document.getElementById("filecontent").value = content;
        document.getElementById("filenamelable").innerHTML = filename;
    };
    sendRequest(req, callback);
}