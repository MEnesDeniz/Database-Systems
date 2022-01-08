function selectFunction(){  
    var x=0;   
    for(x=0;x<5;x++){
    var option = "<option value='" + x + "'>Label " + x + "</option>"
    document.getElementById('selectId').innerHTML += option;   
    } 
} 