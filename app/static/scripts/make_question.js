function uncheck_all_except_one(name){

    var cb = [document.getElementsByName("a1_cb")[0] ,
        document.getElementsByName("a2_cb")[0],
        document.getElementsByName("a3_cb")[0],
        document.getElementsByName("a4_cb")[0]]
    for (var i = 0; i < cb.length; i++) {
        if(cb[i].getAttribute("name") !== name){
            cb[i].checked = false
        }else{
            cb[i].checked = true
        }

    }

}

var slider = document.getElementById("myRange");
var output = document.getElementById("demo");
output.innerHTML = slider.value;

slider.oninput = function() {
    output.innerHTML = this.value;
}