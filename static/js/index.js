var socket = io();
socket.connect("http://127.0.0.1:5000/");
socket.on('connect', function() {
    socket.emit('connected');
});
let buttonContainer = undefined;
let buttonList = undefined;
window.addEventListener('load', function () {
    buttonContainer = document.getElementById("table");
    buttonList = document.getElementsByTagName('button');
    $('.alert-danger').hide();
    $('.alert-success').hide()
    for (let index = 0; index < buttonList.length; index++) {
        const button = buttonList[index];
        if(button.classList.contains('close'))
            continue
        button.addEventListener("click",(e)=>{
            e.preventDefault();
            let id = button.getAttribute("id");
            socket.emit('order',id);
        })
    }
    socket.on('order-response', (data) => {
        if(data.accepted == true){
            $('.alert-success').show()
        }
        else{ $('.alert-danger').show()}
    })
    
  })

window.setTimeout(function() {
    $('.alert-danger').hide();
}, 2000);
window.setTimeout(function() {
    $('.alert-success').hide()
}, 2000);
socket.on('order-response',data=>{
    if(data.accepted == true)
        $('.alert-success').show()
        window.setTimeout(function() {
            $('.alert-success').hide()
        }, 2000);
})
socket.on('order-response',data=>{
    if(data.accepted == false)
        $('.alert-danger').show()
        window.setTimeout(function() {
            $('.alert-danger').hide();
        }, 2000);
})
