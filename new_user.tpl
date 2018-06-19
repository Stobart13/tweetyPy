<html>

<head>
</head>
<style type='text/css'>
      body {background: #00aced; color: #FFF;
        font-family: 'Open Sans', sans-serif;
      }
  </style>

<body>
<div class="container-fluid">
    <div class="jumbotron">
      <form method="POST" action="/newUserStore" class="form-signin">
        <h2 class="form-signin-heading">Create New User</h2>
        <table>
		<tr><td><label for="input" class="sr-only">Name:</label></td>
        <td><input type="text" name="username" class="form-control" placeholder="name" required autofocus></td></tr>
		<tr><td><label for="inputPassword" class="sr-only">Password:</label></td>
        <td><input type="password" name="password" class="form-control" placeholder="Password" required></td></tr>
        <tr><td><button name="save" value="Save" type="submit">Create</button></td>
        </tr>
		</table>
      </form>
    </div>
</div> <!-- /container -->

</body>
</html>