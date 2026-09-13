FROM android:latest

WORKDIR /app

COPY . .

RUN chmod +x ./gradlew

WORKDIR android_remote

RUN ./gradlew assembleRelease --no-daemon

RUN ls -la app/build/outputs/apk/release/
