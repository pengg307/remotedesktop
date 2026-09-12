FROM flutter:3.16.0-stable

# 安装必要工具
RUN apt-get update && apt-get install -y \
    android-sdk-build-tools \
    android-sdk-platform-28 \
    cmake \
    ninja-build \
    git \
    wget \
    curl \
    unzip \
    && flutter precache \
    && flutter doctor --android-licenses \
    && sdkmanager "platforms;android-34" "build-tools;33.0.0" \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

# 获取依赖
RUN cd flutter_remote && flutter pub get

# 构建 APK
RUN cd flutter_remote && flutter build apk --release

# 输出到挂载点
RUN mkdir -p /output && cp flutter_remote/build/app/outputs/flutter-apk/app-release.apk /output/

CMD ["ls", "-la", "/output/"]
