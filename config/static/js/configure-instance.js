// Configuration tab menu
const tabs = document.querySelectorAll('.tabs li');
const tabContentBoxes = document.querySelectorAll('#tab-content > div');
console.log("ca cause?");
tabs.forEach((tab) => {
     tab.addEventListener('click',() => {
         tabs.forEach(item => item.classList.remove('is-active'))
         tab.classList.add('is-active');

         const target = tab.dataset.target;
         console.log(target);
         tabContentBoxes.forEach(box => {
            if (box.getAttribute('id') === target){
                box.classList.remove('is-hidden');
            } else {
                box.classList.add('is-hidden');
            }
         });
    })
})

function STAChange() {
    console.log("STAChange")
    const STAInfo = document.getElementById("STAInfo");
    const obj = JSON.parse(STAInfo.value.replace(/\'/g, '"').replace(/False/g, 'false'));

    console.log("name: "+obj.name+" / url:"+obj.url);
    document.getElementById("STAOwner").value = obj.owner;
    document.getElementById("STAEmail").value = obj.email;
    //document.getElementById("STAUnit").value = obj.unit;
    document.getElementById("STALabel").value = obj.name;
    document.getElementById("STATitle").value = obj.title;
    document.getElementById("STAAbstract").value = obj.abstract;
    document.getElementById("STAUrl").innerHTML = obj.url;
};

function STAChangeCreateMviewer() {
    const STAInfo = document.getElementById("STAInfoCreateMviewer");
    const obj = JSON.parse(STAInfoCreateMviewer.value.replace(/\'/g, '"').replace(/False/g, 'false'));

    console.log("name: "+obj.name+" / url:"+obj.url);
    document.getElementById("STALabelCreateMviewer").value = obj.name;
    document.getElementById("STATitleCreateMviewer").value = obj.title;
    document.getElementById("STAUrlCreateMviewer").innerHTML = obj.url;
};
