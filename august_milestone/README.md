# Foundations to Computer Security

|Sameer Gupta| Lakshay Chauhan  | Chaitanya Arora | Ankit Kumar   |
|:---:|:---:|:---:|:---:|
|2021093|2021060|2021033|2021015|

## Project Description
The Real Estate Aggregator System: The
focus of this project is to create a portal that facilitates the secure exchange and
verification of property-related documents and to enable secure transactions during
property buying/selling/renting.
## August Milestone

Tech Stack:
- Frontend: HTML, CSS, JS
- Backend: Django
- Database: SQLite
- Web Server: Nginx & Gunicorn

> Self signed SSL certificate generated using Certbot and Let's Encrypt.

## Commands used to setup the entire server:

A total of 705 Commands were used to setup the entire server. The commands are listed in the file `commands_history.txt` File.

The sequence of commands used to setup the server is as follows:

1. Installing NGINX and configuring it
```
> sudo apt install nginx
> sudo systemctl start nginx
> sudo systemctl enable nginx
> sudo nano /etc/nginx sites-available/twentyfiveacres
```

then I edited the config file to redirect port 80 to 443 and also added the SSL certificate path. The certificate was generated using Certbot and Let's Encrypt. 

```
> sudo apt install certbot python3-certbot-nginx
> sudo certbot --nginx -d 192.168.2.235
> sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/private/nginx-selfsigned.key -out /etc/ssl/certs/nginx-selfsigned.crt
```

The certificates are located in the `/etc/ssl` directory.
> /etc/ssl/certs/nginx-selfsigned.crt  
> /etc/ssl/private/nginx-selfsigned.key

The final nginx config file looks like this:

![image](https://github.com/ankitkat042/Image-Link-Generator/assets/79627254/ef25906d-33f9-43ab-bb5d-460caa0eb175)

and the SSL certificate looks like this:

![image](https://github.com/ankitkat042/Image-Link-Generator/assets/79627254/b7afcff8-0faf-44b5-a64d-7a3e78587a5c)

2. Installing Django and Gunicorn
```
> pip3 install Django
> mkdir windsor
> cd windsor
> python3 -m venv venv
> source venv/bin/activate
> django-admin startproject > twentyfiveacres
> pip install gunicorn
> sudo nano /etc/systemd/system/> gunicorn.service
> sudo systemctl daemon-reload
> sudo systemctl start gunicorn
```

After this I edited the gunicorn.service file to add the path to the project and the wsgi file.

And finally, I created a html file in Django and ran the server using gunicorn.

You can find some of the debugging commands and file permission commands in the following code block.

```
> sudo nginx -t
> sudo systemctl reload nginx
> sudo journalctl -u gunicorn
> sudo chown www-data:www-data /home/iiitd/windsor/twentyfiveacres/gunicorn.sock
> sudo chmod +x /home/iiitd/windsor
> sudo systemctl restart gunicorn
> sudo systemctl restart nginx
> sudo cat /var/log/nginx/error.log
> sudo chown -R iiitd:www-data /home/iiitd/windsor/twentyfiveacres/
> sudo chmod 750 /home/iiitd/windsor/twentyfiveacres/
> sudo chown iiitd:www-data /home/iiitd/windsor/twentyfiveacres/gunicorn.sock
> sudo chmod 770 /home/iiitd/windsor/twentyfiveacres/gunicorn.sock
```

with this, the Final website looks like this:

![image](https://github.com/ankitkat042/Image-Link-Generator/assets/79627254/75f53909-bd68-41eb-807e-19caf8aafb56)



