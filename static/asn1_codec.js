
var selectedMessage = null;


function postRequest(req, callBack)
{
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function(){
        if (this.readyState == 4 && this.status == 200) {
            var fixedResponse = xmlhttp.responseText.replace(/\\'/g, "'");
            var data = JSON.parse(fixedResponse);
            var status = data["status"];
            var output = data["output"];
            var log = data["log"];
            callBack(status, output, log);
        };
    };
    xmlhttp.open("POST", '/asn1_codec', true);
    xmlhttp.setRequestHeader("Content-Type", "application/json");
    xmlhttp.send(JSON.stringify(req));    
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
    selectedMessage = null;
    var node = document.getElementById("asn_file");
    var fileName = node.files[0];
    var reader = new FileReader();
    reader.onload = function(){
        var req = {'type': 'compile', 'content': reader.result};
        postRequest(req, function(isCompileSuccess, msgList, compileLog){
            showCompileLog(compileLog);
            showMessageList(msgList);
        });
    };
    reader.readAsText(fileName);
}

function getSelectedProtocol()
{
    if (document.getElementById("per").checked) { return 'per'; }
    if (document.getElementById("uper").checked) { return 'uper'; }
    if (document.getElementById("ber").checked) { return 'ber'; }
    if (document.getElementById("der").checked) { return 'der'; }
    if (document.getElementById("cer").checked) { return 'cer'; }
}

function getSelectedFormat()
{
    if (document.getElementById("asn1").checked) { return 'asn1'; }
    if (document.getElementById("json").checked) { return 'json'; }   
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
    var format = getSelectedFormat();
    var req = {"type": "encode",
               "msg_name": selectedMessage,
               "protocol": protocol,
               "format": format,
               "content": input};
    postRequest(req, function(status, outputResult, log){
        var outputBox = document.getElementById("output");
        outputBox.value = outputResult + "\n";
        if (status == false) {
            outputBox.value += "Encode fail!\n";
            outputBox.value += log;
        }
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
    var format = getSelectedFormat();
    var req = {"type": "decode",
               "msg_name": selectedMessage,
               "protocol": protocol,
               "format": format,
               "content": input};
    postRequest(req, function(status, outputResult, log){
        var outputBox = document.getElementById("output");
        outputBox.value = outputResult + "\n";
        if (status == false) {
            outputBox.value += "Decode fail!\n";
            outputBox.value += log;
        }
    });
}

function onSelectedMsgChanged(selectedIndex)
{
    var msgsBox = document.getElementById("msgs");
    selectedMessage = msgsBox.options[selectedIndex].value;
    var req = {"type": "get_msg_definition",
               "msg_name": selectedMessage};
    postRequest(req, function(isDefinitionFounded, definition, log){
        var codeDisplayBox = document.getElementById("code_display");
        if (isDefinitionFounded == true){
            codeDisplayBox.value = definition;
        }
        else{
            codeDisplayBox.value = "Cannot find the definition of this message!\n";
            codeDisplayBox.value += log;
        }
    });
}
