# playing-with-redis

I'ts a simple app to shows how to work with redis in python.

Also implements a Flask Rest API with two entities:

        /users


        /messages

For example:

    - POST /messages/<user_id>/send

            Add a message for an user

    - GET /messages/<user_id>/unread

            Unread messages

    - GET /messages/<user_id>/read
        
            Read messages
            
    - POST /messages/broadcast

        Send a message for all users
