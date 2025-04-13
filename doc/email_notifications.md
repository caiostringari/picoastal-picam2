# Email Notifications

Email notifications allow you to receive updates about the status of your camera system and the latest captured images.

**Warning**: This will require that you store a ```gmail``` user name and password in
plain text in your system. I strongly recommend to use an accounted that you
create exclusively for using the cameras.

After creating the account, create a hidden file named ".gmail" in your home
folder with the login and password.

```
cd ~
nano .gmail
```

Add the following contents:

```json
{
    "credentials": {
      "login": "some.login@gmail.com",
      "destination": "some.email@gmail.com",
      "password": "somepassword"
    },
    "options": {
      "send_log": true,
      "send_last_frame": true,
      "send_average": false,
      "send_deviation:": false
    }
}
```

To save and exit use ```ctrl+o``` + ```ctrl+x```.

Make sure to change gmail's security settings to allow you to send emails using python.