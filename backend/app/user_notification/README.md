

Swagger:
```
tags:
- name: user_notification
  description: Operations about User Notification

paths:
  /user_notifications/:
    get:
      tags:
      - user_notification
      summary: Get All UserNotifications
      description: This can only be done by the logged in user.
      operationId: GetUserNotifications
      responses:
        200:
          description: successful operation
          content:
            application/json:
              schema:
                type: object
                properties:
                  user_notifications:
                    type: array
                    items:
                      $ref: '#/components/schemas/UserNotification'
        401:
          $ref: '#/components/responses/Unauthorized'
    post:
      tags:
      - user_notification
      summary: Add UserNotification
      description: This can only be done by the logged in user.
      operationId: AddUserNotification
      requestBody:
        description: Add user_notification object
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UserNotification'
        required: true
      responses:
        200:
          description: successful operation
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Global'

        400:
          description: Invalid user_notification supplied
          content: {}
        401:
          $ref: '#/components/responses/Unauthorized'
      x-codegen-request-body-name: body
  /user_notifications/{id}:
    get:
      tags:
      - user_notification
      summary: Get user_notification
      description: This can only be done by the logged in user.
      operationId: getUserNotificationById
      parameters:
      - name: id
        in: path
        description: The id that needs to get
        required: true
        schema:
          type: string
      responses:
        200:
          description: successful operation
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Global'
        400:
          $ref: '#/components/responses/BadRequest'
        404:
          description: UserNotifications not found
          content: {}
        401:
          $ref: '#/components/responses/Unauthorized'
    delete:
      tags:
      - user_notification
      summary: Delete user_notification
      description: This can only be done by the logged in user.
      operationId: deleteUserNotification
      parameters:
      - name: id
        in: path
        description: The id that needs to be deleted
        required: true
        schema:
          type: string
      responses:
        200:
          description: successful operation
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Global'
        400:
          $ref: '#/components/responses/BadRequest'
        404:
          description: UserNotification not found
          content: {}
        401:
          $ref: '#/components/responses/Unauthorized'
    patch:
      tags:
      - user_notification
      summary: Updated UserNotification
      description: This can only be done by the logged in user.
      operationId: updateUserNotification
      parameters:
      - name: id
        in: path
        description: ID that need to be updated
        required: true
        schema:
          type: string
      requestBody:
        description: Updated user_notification object
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UserNotification'
        required: true
      responses:
        200:
          description: successful operation
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Global'
        400:
          description: Invalid user_notification supplied
          content: {}
        404:
          description: user_notification not found
          content: {}
        401:
          $ref: '#/components/responses/Unauthorized'
      x-codegen-request-body-name: body
  /user_notifications/user/{user_id}:
    get:
      tags:
      - user_notification
      summary: Get user_notification
      description: This can only be done by the logged in user.
      operationId: getUserNotificationByUserId
      parameters:
      - name: user_id
        in: path
        description: The user id that needs to get
        required: true
        schema:
          type: string
      responses:
        200:
          description: successful operation
          content:
            application/json:
              schema:
                type: object
                properties:
                  user_notifications:
                    type: array
                    items:
                      $ref: '#/components/schemas/UserNotification'
        400:
          description: Invalid user_id supplied
          content: {}
        404:
          description: UserNotifications not found
          content: {}
        401:
          $ref: '#/components/responses/Unauthorized'
    delete:
      tags:
      - user_notification
      summary: Delete All user_notification by User id
      description: This can only be done by the logged in user.
      operationId: deleteAllUserNotificationByUserId
      parameters:
      - name: user_id
        in: path
        description: The user id that needs to be deleted
        required: true
        schema:
          type: string
      responses:
        200:
          description: successful operation
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Global'
        400:
          $ref: '#/components/responses/BadRequest'
        404:
          description: UserNotification not found
          content: {}
        401:
          $ref: '#/components/responses/Unauthorized'
  /user_notifications/user/count/{user_id}:
    get:
      tags:
      - user_notification
      summary: Get Count user_notification
      description: This can only be done by the logged in user.
      operationId: getCountUserNotificationByUserId
      parameters:
      - name: user_id
        in: path
        description: The user id that needs to get
        required: true
        schema:
          type: string
      responses:
        200:
          description: successful operation
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Global'
        400:
          description: Invalid user_id supplied
          content: {}
        404:
          description: UserNotifications not found
          content: {}
        401:
          $ref: '#/components/responses/Unauthorized'
  
  /user_notifications/read/{id}:
    post:
      tags:
      - user_notification
      summary: read user_notification
      description: This can only be done by the logged in user.
      operationId: readUserNotificationById
      parameters:
      - name: id
        in: path
        description: The user id that needs to get
        required: true
        schema:
          type: string
      responses:
        200:
          description: successful operation
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Global'
        400:
          description: Invalid user_id supplied
          content: {}
        404:
          description: UserNotifications not found
          content: {}
        401:
          $ref: '#/components/responses/Unauthorized'
  /user_notifications/read/all/{user_id}:
    post:
      tags:
      - user_notification
      summary: read all user_notification by user id
      description: This can only be done by the logged in user.
      operationId: readAllUserNotificationById
      parameters:
      - name: user_id
        in: path
        description: The user id that needs to get
        required: true
        schema:
          type: string
      responses:
        200:
          description: successful operation
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Global'
        400:
          description: Invalid user_id supplied
          content: {}
        404:
          description: UserNotifications not found
          content: {}
        401:
          $ref: '#/components/responses/Unauthorized'
components:
  schemas:
    UserNotification:
      type: object
      properties:
        id:
          type: string
          format: uuid
        name:
          type: string
        user_id:
          type: integer
          format: int64
        read:
          type: boolean
        timestamp:
          type: string
          format: date-time
        message:
          type: string
```