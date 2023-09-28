async function postData(url = "",data = {}) {
    const response = await fetch(url, {
          method: "POST",
          headers: {
          "Content-Type": "application/json"
          },
          body: JSON.stringify(data),
      });
      if (response.status == 201 || response.status == 200) {
              return response.headers;
      } else {
          return false
      }
    }

async function startOgcApi(dataInput,processName) {
    _processing = true; // a mettre en place pour ne pas double lancer un process
     _ogcApiUrl="https://geosas.fr/sofair-dev/api/processes/"
    //_ogcApiUrl="/proxy/?url=https://api.geosas.fr/sofair/processes/"
    postUrl = _ogcApiUrl+processName+"/execution"

    //ogcApiProcessUrl='/proxy/?url='+_ogcApiUrl+ProcessName+"/execution"
    console.log("start query process")
    data_status = await postData(postUrl, dataInput)

    if (data_status == false) {
        console.log("error process, ",processName);
        alert("Le serveur ne repond pas")
        _processing = false
        return false
    } else {
        console.log("process accepted")
        //location_I='/proxy/?url='+data_status.get('location')+"?f=json"
        //location_R='/proxy/?url='+data_status.get('location')+"/results?f=json"

        location_I=data_status.get('location')+"?f=json"
        location_R=data_status.get('location')+"/results?f=json"

        data_process_out = await fetch(location_I)
            .then((response) => response.json())
            .then((data_location) =>   {
                console.log("check process")
                console.log(data_location['progress'])

                if (data_location['status']=='failed'){
                    console.log("process failed")
                    return false
                } else {
                    return data_location
                }
            })
        console.log("new")
        console.log(data_process_out['progress'])
        if (data_process_out==false){
            return data_process_out
        } else {

            while (data_process_out['progress'] != 100 ){
                await new Promise(resolve => setTimeout(resolve, 2000));
                data_process_out = await fetch(location_I).then((response) =>   { return response.json()})

                console.log(data_process_out['progress'])
            }
        }
        console.log("requete terminée")
        data_process_out = await fetch(location_R).then((response) =>   { return response.json()})
        console.log(data_process_out)
        //plot_culture(0,data_process_out)
        _processing = false
        return data_process_out
    }

}