# playing-with-redis

I'ts a simple app to shows how to work with redis in python.

Also implements a Flask Rest API with two entities:

        /users


        /notifications

For example:

    - POST /notifications/send/<user_id>

            Add a notification for an user

    - POST /notifications/broadcast

        Send a notification for all users
