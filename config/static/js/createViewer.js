async function createViewer () {
    console.log ("async function createInstance")
    console.log ("async function createInstance")
    ogcApiUrl = "https://geosas.fr/sofair-dev/api/processes/"
    processName = "create-viewer"
    postUrl = ogcApiUrl+processName+"/execution"
    console.log ("Function createViewer -> "+postUrl)
    document.getElementById("createViewerButton").classList.add('is-loading')
    url_sensorthings = document.getElementById('STAUrlCreateMviewer').textContent

    data_input ={
      "inputs": {
        "url_sensorthings":url_sensorthings
      }
    }
    console.log (JSON.stringify(data_input))
    var response = await startOgcApi(data_input, processName)
    /*var response = await fetch(postUrl, {
          method: "POST",
          headers: {
          "Content-Type": "application/json",
          },
         body: JSON.stringify(data_input)
    });*/
    console.log(response)
    alert(response['url_mviewer'])
    alert(response['url_config'])
    document.getElementById("createViewerButton").classList.remove('is-loading')
};