Для работы приложения необходимо сгенерировать приватный и публичный ключ для создания и проверки JWT токенов.
Это можно сделать с помощью утилиты `openssl` следующими командами:

- Приватный ключ:

```bash
openssl genpkey -algorithm RSA -out ./certs/private_key.pem -pkeyopt rsa_keygen_bits:2048
```

- Публичный ключ:

```bash
openssl rsa -pubout -in ./certs/private_key.pem -out ./certs/public_key.pem
```
