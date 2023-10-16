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
    var name = document.getElementById('STACreationName').value
    var title = document.getElementById('STACreationTitle').value
    var abstract = document.getElementById('STAAbstract').value
    var email = document.getElementById('STAEmail').value
    var author = document.getElementById('STAAuthor').value
    data ={
      "inputs": {
        "name": name,
        "title": title,
        "abstract": abstract,
        "author": author,
        "email":email
      }
    }
    console.log (JSON.stringify(data))
    var response = await startOgcApi(data, processName)
    console.log(response)

    document.getElementById("createInstanceButton").classList.remove('is-loading')
    //alert(response['STAUrl'])
    location.replace ("https://geosas.fr/sofair-dev/#" + name)
};
