Issues:

## Redis

chmod 644 redis.conf
<https://github.com/redis/docker-library-redis/issues/120#issuecomment-430049839>

## Django

Add to host

<https://stackoverflow.com/questions/40582423/how-to-fix-django-error-disallowedhost-at-invalid-http-host-header-you-m>

## phpMyAdmin (Deployed)

Uncaught SyntaxError: Unexpected token '<'
phpmyadmin:55 Uncaught ReferenceError: CommonParams is not defined
    at phpmyadmin:55:1

Potential Solution: Verify PHP and Apache Configuration
Ensure that the PHP files are being processed correctly by Apache. In your Apache configuration, ensure you have the following (or similar) settings in your .conf file:
apache

``` conf
<Directory /path/to/phpmyadmin>
    Options Indexes FollowSymLinks
    AllowOverride All
    Require all granted
</Directory>

AddType application/x-httpd-php .php
```
