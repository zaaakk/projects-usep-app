#### overview

This is the code that powers the Brown University [U.S. Epigraphy](http://library.brown.edu/projects/usep/) project.

For more information about that project, see that site's ['About' page](http://library.brown.edu/projects/usep/about/)

---

#### student-developer installation

- mac

    - note: this first write-up will go through steps very sequentially; much can be optimized in the future via a provision shell-script.

    - assumptions

        - you have [Brown's VPN](https://www.brown.edu/information-technology/software/catalog/vpn-f5-desktop-client) installed, and active

        - you have python 2.7x, [virtualenv](https://virtualenv.pypa.io/en/stable/) -- all modern macs default to this

        - you have [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git#Installing-on-Mac) installed

        - you have [virtualenv](https://virtualenv.pypa.io/en/stable/installation/) installed

        - mild familiarity with the Terminal app (when you see an instruction to run something that begins with a `$`, that means run it from the Terminal -- but don't type the `$` and following space)

        - xcode developer tools are installed

            - why: needed to install lxml, a python xml package, in a later step

            - if you're not sure they're installed, try running `$ xcode-select --install`

                - if the developer tools weren't installed, you'll be prompted to install them via a GUI interface -- takes 5-10 minutes for the install

    - create the directory 'usepweb_project_stuff' anywhere (not web-accessible)

    - create the virtual environment

        -  cd into the `usepweb_project_stuff` directory, and run:

                $ virtualenv --python=/usr/bin/python2.7 --prompt=[env_usepweb] --no-site-packages ./env_usepweb

        - you should now see the directory `env_usepweb` in the `usepweb_project_stuff` directory

    - activate the virtual environment

        - run `$ source ./env_usepweb/bin/activate`

            - you'll notice the beginning of the command-line now shows `[env_usepweb]`, indicating that the virtual environment is activated.

        - run `$ pip install pip --upgrade`

            - [pip](https://pypi.python.org/pypi/pip) is a tool for installing python packages

    - get this code

        - run `$ git clone https://github.com/Brown-University-Library/usepweb_project ./usepweb_project`

        - you should now see the directory `env_usepweb`, and the directory `usepweb_project`, in the `usepweb_project_stuff` directory

    - update the virtual environment

        - run `$ pip install -r ./usepweb_project/config/requirements.txt`

        - takes a few minutes; if you want, you can see the packages you just installed with the command `$ pip freeze` (you don't have to run that)

    - make some directories

        - run `$ mkdir ./usepweb_logs`

        - run `$ mkdir ./usepweb_env_settings`

        - run `$ mkdir ./usepweb_db_stuff`

        - run `$ mkdir ./usepweb_web_stuff`

        - you should now see those four directories, in addition to the previous two, in the `usepweb_project_stuff` directory

    - create the environmental-settings file

        - get the `usepweb_env_settings.sh` file from a developer, and put it in the `usepweb_env_settings` directory

        - open the file `env_usepweb/bin/activate`, and add the following 3 lines to the bottom (replacing `FULL_PATH_TO` with your actual path:

                USEPWEB__SETTINGS="/FULL_PATH_TO/usepweb_env_settings.sh"
                source $USEPWEB__SETTINGS
                echo "- usepweb_project env settings loaded into environment from $USEPWEB__SETTINGS"

            (tip: you can copy the full path to a file by selecting the file in the Finder, and selecting option-command-c)

        - load the settings file by running

                $ source ./env_usepweb/bin/activate

            (you'll see the `echo` message appear)

    - db work

        - create the db:

                $ sqlite3 ./usepweb_db_stuff/usepweb.db
                SQLite version 3.8.10.2 2015-05-20 18:17:19
                Enter ".help" for usage hints.
                sqlite> create table dummy(text, priority INTEGER);
                sqlite> drop table dummy;
                sqlite> .quit
                $

            - the db is not actually saved until a table is created, thus the dummy table create/drop

        - update the db's structure

            - navigate into the project directory

                - run `$ cd ./usepweb_project/`

                you're now in the `usepweb_project_stuff/usepweb_project` directory

            - initial db setup

                - run `$ python ./manage.py migrate`

            - additional db setup

                - run `python ./manage.py migrate --run-syncdb`

    - prepare localhost web-data

        - create, in your web-accessible directory, the directory `usep_web_stuff`, and cd into it.

        - data

            - run `$ git clone https://github.com/Brown-University-Library/usep-data.git ./usep_data`

        - media

            - run `$ mkdir ./usep_media`

            - cd back to your project-directory (not the 'stuff' directory)

                run `$ ./manage.py collectstatic --clear`, and after confirming it will write to the correct directory, type 'yes'

            - note: normally this step does not have to be done when using django's development webserver, but has to in this case because of the javascript xslt work. _TODO: investigate whether this can be done without collectstatic._

        - images (not absolutely necessary, but useful)

            - run `$ mkdir ./usep_images` and and copy images files from the development server that start with CA.Berk...

            - _TODO: see if we can point to the dev-server's image directory_


---

#### provisioning TODOs

- combine some of above into a shell script

- consider a pre-made sqlite3 db

---
