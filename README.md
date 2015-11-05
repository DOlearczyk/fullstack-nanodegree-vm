# Tournament planner
=============
Tournament planner allows to create and conduct a swiss-system tournament.

## Requirements

You have to have [VirtualBox](https://www.virtualbox.org/) and [Vagrant](https://www.vagrantup.com/) installed. Also you need psycopg2 package.

##Installation

Download the repository. Next use command line like Git Bash to navigate to vagrant folder and type commands:
```
vagrant up
vagrant ssh
```
Then change directory by writing `cd /vagrant` and `cd tournament`. Type `psql` to access postgresql database and write `\i tournament.sql` to create tournament database. Then go back by `\q` command and use command `python tournament_test.py` to test.



