##### overview

This is the code that powers the Brown University [U.S. Epigraphy](http://library.brown.edu/projects/usep/) project.

For more information about that project, see that site's ['About' page](http://library.brown.edu/projects/usep/about/)

---

#### student-developer installation

- mac

    - assumptions

        - you have [Brown's VPN](https://www.brown.edu/information-technology/software/catalog/vpn-f5-desktop-client) installed

        - python 2.7x, [virtualenv](https://virtualenv.pypa.io/en/stable/), and [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git#Installing-on-Mac) are installed

        - mild familiarity with the Terminal app (when you see an instruction to run something that begins with a `$`, that means run it from the Terminal, but don't type the `$` and following space)

        - xcode developer tools are installed

            - why: needed to install lxml, a python xml package, in a later step

            - if you're not sure they'e installed, try running `$ xcode-select --install`

                - if the developer tools weren't installed, you'll be prompted to install them via a GUI interface -- takes 5-10 minutes for the install

    - create the directory 'usepweb_project_stuff' anywhere

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

        - run `$ `

    - make a log directory and an env_settings directory

        - run `$ mkdir ./usepweb_logs`

        - run `$ mkdir ./usepweb_env_settings`

        - you should now see those two directories, in addition to the previous two, in the `usepweb_project_stuff` directory


    - to be continued...

---
