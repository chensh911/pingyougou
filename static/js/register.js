$(function(){

	var error_name = false;
	var error_password = false;
	var error_check_password = false;
	var error_check = true;


	$('#username').blur(function() {
		check_user_name();
	});

	$('#password').blur(function() {
		check_pwd();
	});

	$('#re-password').blur(function() {
		check_cpwd();
	});


	$('#allow').click(function() {
		if($(this).is(':checked'))
		{
			error_check = false;
			$(this).next('i').hide();
		}
		else
		{
			error_check = true;
			$(this).next('i').html('请勾选同意');
			$(this).next('i').show();
		}
	});


	function check_user_name(){
		var len = $('#username').val().length;
		if(len<5||len>20)
		{
			$('#username').prev().html('请输入5-20个字符的用户名')
			$('#username').prev().show();
			error_name = true;
		}
		else
		{
			$('#username').prev().hide();
			error_name = false;
		}
	}

	function check_pwd(){
		var len = $('#password').val().length;
		if(len<8||len>20)
		{
			$('#password').prev().html('密码最少8位，最长20位')
			$('#password').prev().show();
			error_password = true;
		}
		else
		{
			$('#password').prev().hide();
			error_password = false;
		}
	}


	function check_cpwd(){
		var pass = $('#password').val();
		var cpass = $('#re-password').val();

		if(pass!=cpass)
		{
			$('#re-password').prev().html('两次输入的密码不一致')
			$('#re-password').prev().show();
			error_check_password = true;
		}
		else
		{
			$('#re-password').prev().hide();
			error_check_password = false;
		}

	}



	$('#reg_form').submit(function() {
		check_user_name();
		check_pwd();
		check_cpwd();
		if(error_name == false && error_password == false && error_check_password == false && error_check == false)
		{
			return true;
		}
		else
		{
			return false;
		}

	});








})