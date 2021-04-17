#!/bin/sh
curl -X POST \
-H "Authorization: Bearer "$(gcloud auth application-default print-access-token) \
-H "Content-Type: application/json; charset=utf-8" \
-d "{
  \"input\":{
    \"text\":\"$1\"
  },
  \"voice\":{
    \"languageCode\":\"en-us\",
    \"name\":\"en-US-Wavenet-C\",
    \"ssmlGender\":\"FEMALE\"
  },
  \"audioConfig\":{
    \"audioEncoding\":\"MP3\"
  }
}" \
https://texttospeech.googleapis.com/v1/text:synthesize | jq -r ".audioContent" | base64 --decode > $2





