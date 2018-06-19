<html>

<head>
<style type="text/css">
   body {background: #00aced;
        font-family: 'Open Sans', sans-serif; }
   p { border:solid 1px #888;width:300px; padding:100px; 
	   background-color:#ffe;
	   margin:auto; margin-top:100px; text-align:center; font-weight:bold; }
   .link { text-align:center; margin-top:20px; }
   a{ color: #fff; text-decoration: none; }
   a:hover{text-decoration: underline;}	   
</style>
</head>

<body>

<p>
Hi there <strong>{{name}}</strong>
<br>
{{message}}
%if success==True:
<br>Number of logins: {{logins}}
%end
</p>
%if success==False:
<div class="link">
<a href="/login">Try again</a>
</div>
%end

<div class="link">
<a href="/logout">Logout</a>
</div>
			  
</body>
</html