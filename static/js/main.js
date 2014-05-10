$( document ).ready(function(){
    //// Add listeners
    $('#slow').click(submitForm);
    $('#slow-swatch').click(submitForm);
    $('#medium').click(submitForm);
    $('#medium-swatch').click(submitForm);
    $('#fast').click(submitForm);
    $('#fast-swatch').click(submitForm);
    $('#on').click(submitForm);
    $('#on-swatch').click(submitForm);
    $('#off').click(submitForm);
    $('#off-swatch').click(submitForm);


});

function submitForm() {
    $(".bottom-menu").css({"display": "none"})
    $(".top-menu").css({"display": "none"})
    $(".loading").css({"display": "block"})
    console.log("submitting: , ", this.id)
    url = "/mode"
    xsrf =  getCookie("_xsrf")
    data = {'_xsrf': xsrf}
    data[this.id] = this.id
    console.log("json: ", data)
    $.ajax({type: "POST",
        url: url,
        data: data,
        success: success,
        error: error,
        dataType: "json"}
        )
}


function success(msg) {
    console.log(msg)
    if (msg['file_transfer'] == "finished") {
        $(".bottom-menu").css({"display": "block"})
        $(".top-menu").css({"display": "block"})
        $(".loading").css({"display": "none"})
        console.log("huzzah!")
    }
    console.log(msg)
}

function error(jqXHR, status, exception) {
    alert("Error encountered updating the sign server: ", status)
    console.log(jqXHR)
    console.log(exception)
}
