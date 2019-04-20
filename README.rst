Para instalar la apliacacion en modo desarrollo debera seguir los siguientes pasos:

1-) Instalar el controlador de versiones git:
    
    $ su

    # aptitude install git

2-) Descargar el codigo fuente del proyecto UserManager:

    Para descargar el código fuente del proyecto contenido en su repositorio GIT realice un clon del proyecto UserManager, como el certificado digital del servidor está autofirmado entonces debemos saltar su chequeo con el siguiente comando:

    GNU/Linux:

    $ export GIT_SSL_NO_VERIFY=True

    Win :

    > git config --global http.sslCAPath "$HOME/.gitcerts"

    $ git clone https://gitlab.com/nikeven/factura_timg.git

3-) Crear un Ambiente Virtual:

    El proyecto está desarrollado con el lenguaje de programación Python, se debe instalar Python v3.5.x Con los siguientes comandos puede instalar Python y PIP.

    Entrar como root para la instalacion 

    # aptitude install python3.5 python3-pip python3.5-dev python3-setuptools

    # aptitude install python3-virtualenv virtualenvwrapper

    Salir del modo root y crear el ambiente:

    $ mkvirtualenv --python=/usr/bin/python3 UserManager

4-) Instalar los requerimientos del proyecto 

    Para activar el ambiente virtual UserManager ejecute el siguiente comando:

    $ workon UserManager
    (UserManager)$

    Entrar en la carpeta raiz del proyecto:

    (UserManager)$ cd UserManager
    (UserManager)UserManager$ 

    Desde ahi se deben instalar los requirimientos del proyecto con el siguiente comando:

    (UserManager)$ pip install -r requerimientos.txt

    De esta manera se instalaran todos los requerimientos iniciales para montar el proyecto 
    
    Nota: Si hay problemas en la instalación del paquete lxml==3.6.0 descrito en el fichero requirements.txt es
    necesario instalar los siguientes paquetes como usuario root:

    # apt-get install python3-lxml
    
    # apt-get install libxml2-dev libxslt-dev python-dev

    # apt-get build-dep python3-lxml

    Luego ejecutamos de nuevo el siguiente comando:

    (UserManager)$ pip install -r requerimientos.txt

5-) Crear base de datos y Migrar los modelos:

    El manejador de base de datos que usa el proyecto es postgres, es necesario, crear la base de datos desde postgres de la siguiente manera si se usa la consola de postgres:

    postgres=# CREATE DATABASE user_manager OWNER=postgres ENCODING='UTF−8';

    Para migrar los modelos del proyecto se debe usar el siguiente comando:

    (UserManager)$ python manage.py makemigrations
    (UserManager)$ python manage.py migrate

    5.1-) Migraciones individuales

        (UserManager)$ python manage.py makemigrations boletas
        (UserManager)$ python manage.py makemigrations certificados
        (UserManager)$ python manage.py makemigrations conectores
        (UserManager)$ python manage.py makemigrations facturas
        (UserManager)$ python manage.py makemigrations folios
        (UserManager)$ python manage.py makemigrations users
        (UserManager)$ python manage.py makemigrations utils

        (UserManager)$ python manage.py migrate

6-) Cargar data inicial del proyecto 

    Asegurese de que los modelos esten migrados en base de datos y ejecute los siguientes comando para cargar la data inicial del proyecto:

    Esto permitira cargar los datos de los estados, municipios y parroquias:
    (UserManager)$ python manage.py loaddata fixtures/initial_data_utils.json
    
    Esto permitira cargar los grupos de usuarios y permisos de los usuarios y el superusuario:
    (UserManager)$  python manage.py loaddata fixtures/initial_data_auth.json



7-) Correr la aplicacion UserManager

    Para correr la apliacion se debe  ejecutar el siguiente comando:

    (UserManager)$ python manage.py runserver

Ingresar a la plataforma con la siguientes credenciales:

Username: admin

password: 1234567890admin
