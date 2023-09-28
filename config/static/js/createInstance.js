function APIServiceChange() {
    console.log("APIServiceChange")
    const APIService = document.getElementById("APIService");
    const obj = JSON.parse(APIService.value.replace(/\'/g, '"').replace(/False/g, 'false'));

    console.log("name: "+obj.name+" / url:"+obj.url);
    document.getElementById("APIServiceUrl").innerHTML = obj.url;
};

async function createInstance () {
    ogcApiUrl = "https://geosas.fr/sofair-dev/api/processes/"
    processName = "create-sta"
    postUrl = "/proxy/?url="+ogcApiUrl+processName+"/execution"
    console.log ("Function createInstance -> "+postUrl)
    document.getElementById("createInstanceButton").classList.add('is-loading')
    var url = document.getElementById('APIServiceUrl').textContent
    var abstract  = document.getElementById('STAAbstract').textContent
    var author = document.getElementById('STAAuthor').value
    var title = document.getElementById('STACreationTitle').value
    var name = document.getElementById('STACreationName').value
    data ={
      "inputs": {
        "name": name,
        "description": title,
        "author": author
      }
    }
    console.log (JSON.stringify(data))
    var response = await startOgcApi(data, processName)
    /*
    var response = await fetch(postUrl, {
          method: "POST",
          headers: {
          "Content-Type": "application/json",
          },
          body: JSON.stringify(data)
    });
    */
    console.log(response)
    alert(response['STAUrl'])
    document.getElementById("createInstanceButton").classList.remove('is-loading')
};
