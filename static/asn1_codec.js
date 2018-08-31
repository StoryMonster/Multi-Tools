
var selectedMessage = null;


function postMsgDefinitionReq(req, callBack)
{
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function(){
        if (this.readyState == 4 && this.status == 200) {
            var fixedResponse = xmlhttp.responseText.replace(/\\'/g, "'");
            var data = JSON.parse(fixedResponse);
            var isDefinitionFounded = data["status"];
            var definition = data["defintion"];
            callBack(isDefinitionFounded, definition);
        };
    };
    xmlhttp.open("POST", '/asn1_codec', true);
    xmlhttp.setRequestHeader("Content-Type", "application/json");
    xmlhttp.send(JSON.stringify(req));
}


function onSelectedMsgChanged(selectedIndex)
{
    var msgsBox = document.getElementById("msgs");
    selectedMessage = msgsBox.options[selectedIndex].value;
    var req = {"type": "get_msg_definition",
               "msg_name": selectedMessage};
    postMsgDefinitionReq(req, function(isDefinitionFounded, definition){
        var codeDisplayBox = document.getElementById("code_display");
        if (isDefinitionFounded == true){
            codeDisplayBox.value = definition;
        }
        else{
            codeDisplayBox.value = "Cannot find the definition of this message!"
        }
    });
}

function onAsn1CodecWindowLoad()
{
    var inputBoxStyle = document.getElementById('input').style;
    inputBoxStyle.height = window.innerHeight * 0.4 + "px";
    inputBoxStyle.width = window.innerWidth * 0.5 + "px";
    var outputBoxStyle = document.getElementById('output').style;
    outputBoxStyle.height = window.innerHeight * 0.4 + "px";
    outputBoxStyle.width = window.innerWidth * 0.5 + "px";
    var msgListStyle = document.getElementById("msgs").style;
    msgListStyle.width = window.innerWidth * 0.2 + "px";
    msgListStyle.height = window.innerHeight * 0.87 + "px";
    var codeDisplayBoxStyle = document.getElementById("code_display").style;
    codeDisplayBoxStyle.width = window.innerWidth * 0.26 + "px";
    codeDisplayBoxStyle.height = window.innerHeight * 0.87 + "px";
}

function onAsn1CodecWindowResize()
{
    onAsn1CodecWindowLoad();
}

function postFileContent(req, callBack)
{
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function(){
        if (this.readyState == 4 && this.status == 200) {
            var fixedResponse = xmlhttp.responseText.replace(/\\'/g, "'");
            var data = JSON.parse(fixedResponse);
            var isCompileSuccess = data["status"];
            var msgList = data["msgs"];
            var compileLog = data["log"];
            selectedMessage = null;
            callBack(isCompileSuccess, compileLog, msgList);
        };
    };
    xmlhttp.open("POST", '/asn1_codec', true);
    xmlhttp.setRequestHeader("Content-Type", "application/json");
    xmlhttp.send(JSON.stringify(req));
}


function showCompileLog(compileLog)
{
    var outputBox = document.getElementById("output");
    outputBox.value = compileLog;
}

function showMessageList(msgList)
{
    var msgsBox = document.getElementById("msgs");
    for (var i = 0; i < msgsBox.options.length;)
    {
        msgsBox.remove(msgsBox.options[i]);
    }
    msgList.forEach(function(msg, index, array){
        var opt = document.createElement("option");
        opt.appendChild(document.createTextNode(msg));
        msgsBox.appendChild(opt);
    });
}

function onCompileClicked()
{
    var node = document.getElementById("asn_file");
    var fileName = node.files[0];
    var reader = new FileReader();
    reader.onload = function(){
        var req = {'type': 'compile', 'content': reader.result};
        postFileContent(req, function(isCompileSuccess, compileLog, msgList){
            showCompileLog(compileLog);
            if (isCompileSuccess == true)
            {
                showMessageList(msgList);
            }
        });
    };
    reader.readAsText(fileName);
}

function postEncodeOrDecodeRequest(req, callBack)
{
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function(){
        if (this.readyState == 4 && this.status == 200) {
            var fixedResponse = xmlhttp.responseText.replace(/\\'/g, "'");
            var data = JSON.parse(fixedResponse);
            var isSuccess = data["status"];
            var output = data["output"];
            callBack(isSuccess, output);
        };
    };
    xmlhttp.open("POST", '/asn1_codec', true);
    xmlhttp.setRequestHeader("Content-Type", "application/json");
    xmlhttp.send(JSON.stringify(req));
}

function getSelectedProtocol()
{
    if (document.getElementById("per").checked) { return 'per'; }
    if (document.getElementById("uper").checked) { return 'uper'; }
    if (document.getElementById("ber").checked) { return 'ber'; }
    if (document.getElementById("der").checked) { return 'der'; }
    if (document.getElementById("oer").checked) { return 'oer'; }
}

function onEncodeClicked()
{
    if (selectedMessage == null)
    {
        alert("Must choose a message!");
        return;
    }
    var input = document.getElementById("input").value;
    var protocol = getSelectedProtocol();
    var req = {"type": "encode",
               "msg_name": selectedMessage,
               "protocol": protocol,
               "content": input};
    postEncodeOrDecodeRequest(req, function(status, outputResult){
        var outputBox = document.getElementById("output");
        outputBox.value = outputResult + "\n";
        if (status == false) { outputBox.value += "Encode fail!"; }
    });
}

function onDecodeClicked()
{
    if (selectedMessage == null)
    {
        alert("Must choose a message!");
        return;
    }
    var input = document.getElementById("input").value;
    var protocol = getSelectedProtocol();
    var req = {"type": "decode",
               "msg_name": selectedMessage,
               "protocol": protocol,
               "content": input};
    postEncodeOrDecodeRequest(req, function(status, outputResult){
        var outputBox = document.getElementById("output");
        outputBox.value = outputResult + "\n";
        if (status == false) { outputBox.value += "Decode fail!"; }
    });
}
