
// CHAT BOOT MESSENGER////////////////////////


$(document).ready(function(){
    $(".chat_on").click(function(){
        $(".Layout").toggle();
        $(".chat_on").hide(300);
    });
    
       $(".chat_close_icon").click(function(){
        $(".Layout").hide();
           $(".chat_on").show(300);
    });
    
});

// data sending tech
// $('#mymessage').on('keyup keypress', function (e) {
// 	var keyCode = e.keyCode || e.which;
// 	var text = $("#mymessage").val();
	
// 	if (keyCode === 13) {
// 		if (text == "" || $.trim(text) == '') {
// 			e.preventDefault();
// 			return false;
//     } else {
//             e.preventDefault();
//             setUserResponse(text);
// 			socket.send(text);
// 			$("#mymessage").blur();	
// 			socket.on('message', function (msg) {
// 				setBotResponse(msg);
// 			});
			
// 			return false;
// 		}
// 	}
// });

// $('#sendbutton').on('click', function (e) {
// 	var text = $("#mymessage").val();
// 	if (text == "" || $.trim(text) == '') {
// 		e.preventDefault();
// 		return false;
//     } else {
//         e.preventDefault();
// 		setUserResponse(text);
// 		socket.send(text);
// 		$("#mymessage").blur();	
// 		socket.on('message', function (msg) {
// 			setBotResponse(msg);
// 		});
// 		return false;
// 		}
// });	

function setUserResponse(val) {
	var UserResponse = '<img class="userAvatar" src=' + "../static/img/userAvatar.jpg" + '><p class="userMsg">' + val + ' </p><div class="clearfix"></div>';
	$(UserResponse).appendTo('.chats').show('slow');
	$("#mymessage").val('');
	scrollToBottomOfResults();
}

function scrollToBottomOfResults() {
	var terminalResultsDiv = document.getElementById('chats');
	terminalResultsDiv.scrollTop = terminalResultsDiv.scrollHeight;
}

function setBotResponse(val) {
			var BotResponse = '<img class="botAvatar" src="../static/img/botAvatar.png"><p class="botMsg">' + val + '</p><div class="clearfix"></div>';
			$(BotResponse).appendTo('.chats').hide().fadeIn(1000);
			scrollToBottomOfResults();
}