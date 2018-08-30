

function onJsonFormaterPageLoad()
{
    var inputBoxStyle = document.getElementById('input').style;
    inputBoxStyle.height = window.innerHeight * 0.9 + "px";
    inputBoxStyle.width = window.innerWidth * 0.45 + "px";
    var outputBoxStyle = document.getElementById('output').style;
    outputBoxStyle.height = window.innerHeight * 0.9 + "px";
    outputBoxStyle.width = window.innerWidth * 0.45 + "px";
}

function onJsonFormaterPageResize()
{
    onJsonFormaterPageLoad();
}