## HTML Tags counter

### Quick Start

* Clone the repo
  ```
  $ git clone https://github.com/maryna-hankevich/tags-counter.git
  $ cd tags-counter
  ```

* Initialize and activate a virtualenv:
  ```
  $ virtualenv --no-site-packages env
  $ source env/bin/activate
  ```

* Install the dependencies:
  ```
  $ pip install -r requirements.txt
  ```

* Run via GUI:
  ```
  $ python app.py 
  ```

* Get tags number via CLI:
  ```
  $ python app.py --get https://google.com
  ```

* Get tags number from sqlite cache via CLI:
  ```
  $ python app.py --view https://google.com
  ```