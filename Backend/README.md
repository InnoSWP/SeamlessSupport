# API

### Functionality
* `/api/v1/users`
  * `GET`. Get user data. Require json with `email`
    * Return json with user `email` and hashed `password`
  * `POST`. Create new user Require json with `email`
    * Return empty json
* `/api/v1/question/`
  * `POST`. Create new question and send it to telegram chat. Require json with `question` and `user_email`
    * Return empty json
* `/api/v1/volunteers/<int:volunteer_id>`
  * `POST`. Volunteer accepted some question. Require json with `channel_message_id` and `user_message_id`
    * Return empty json
  * `GET`. Return list of open user questions.
    * Return list
  * `DELETE`. Cancel opened question.
    * Return empty json


# Firebase
### Configure

1. Create project on [Firebase](https://console.firebase.google.com)
2. Open `Project settings` -> `Service account` -> `Python` -> `Generate new private key`
3. Save key as `seamless-support-firebase-adminsdk.json` on the same level as this file
4. Open `.env` (or environment variables) and set:
```dotenv
DATABASE_URL=https://<YOUR_PROJECT>.firebaseio.com/
PASSWORD_ALPHABET=SYMBOLS_ACCEPTED_IN_PASSWORD
SALT=SALT_FOR_PASSWORD
BOT_TOKEN=1111111111:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
CHANNEL_ID=-1000000000000
```
5. Open `Realtime Database` -> `Rules` and edit file so that it will look like this.
```json
{
  "rules": {
    ".read": false,
    ".write": false,
    "users": {
      ".indexOn": ["email"]
    },
    "questions": {
      "open": {
        ".indexOn": ["volunteer_id"]
      }
    }
  }
}
```


